# !/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio, aiofiles
import os, sys
import re
import math
import logging
from platform import platform
from functools import wraps

import numpy as np
from pixivpy_async.sync import PixivClient
from pixivpy_async.sync import AppPixivAPI
# from pixivpy3 import AppPixivAPI

from FileOperate import zipFile, saveText, formatFileName, makeDirs, timer, findFile
from Translate import getLanguage
from TokenRoundRobin import TokenRoundRobin
from configuration import Pixiv_Tokens, setTimeInDefaultPath, monthNow

sys.dont_write_bytecode = True
_TEST_WRITE = False
tokenPool = TokenRoundRobin(Pixiv_Tokens)


class AsyncIterator:
	def __init__(self, obj):
		self._it = iter(obj)

	def __aiter__(self):
		return self

	async def __anext__(self):
		try:
			value = next(self._it)
		except StopIteration:
			raise StopAsyncIteration
		return value


# def formatFileName(text):
# 	text = re.sub('[/\:*?"<>|]', ' ', text)
# 	text = text.replace('  ', '')
# 	return text

def saveFileCheck(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		arg = args[0]
		(dir, name) = os.path.split(arg)  # 分离文件名和目录名
		if not os.path.exists(dir):
			os.makedirs(dir)
		name = formatFileName(name)
		path = os.path.join(dir, name)
		r = func(*args, **kwargs)
		return r
	return wrapper


# @timethis
@saveFileCheck
async def saveText(path, text):
	name = os.path.basename(path)
	try:
		async with aiofiles.open(path, "w", encoding="UTF8") as f:
			await f.write(text)
		print(f"已保存：【{name}】")
		return path
	except IOError:
		print(f"保存失败：[{name}】")
		return None
		
		
# @timethis
async def openText(path):
	try:
		async with aiofiles.open(path, "r", encoding="UTF8") as f:
			text = await f.read()
	except UnicodeError:
		try:
			async with aiofiles.open(path, "r", encoding="GBK") as f:
				text = await f.read()
		except UnicodeError:  # Big5 似乎有奇怪的bug，不过目前似乎遇不到
			async with aiofiles.open(path, "r", encoding="BIG5") as f:
				text = await f.read()
	finally:
		name = os.path.basename(path)
		# print(name, sep="\n")
		return text
	
@timer
async def copymain():
	path = r"D:\OneDrive - yangtzeu.edu.cn\写作\小说"
	l = findFile(path, ".txt")
	
	async for file in AsyncIterator(l):
		text = await openText(file)
		path = os.path.join("..","N2", os.path.basename(file))
		await saveText(path, text)


async def getNovelInfo(novel_id):
	json_result = tokenPool.getAPI().novel_detail(novel_id)
	# print(json_result)
	novel = json_result.novel
	title = novel.title
	view = novel.total_view
	bookmarks = novel.total_bookmarks
	comments = novel.total_comments
	
	image_urls = novel.image_urls
	text_length = novel.text_length
	return title, view, bookmarks, comments

async def getNovelText(novel_id):
	json_result = tokenPool.getAPI().novel_text(novel_id)
	text = f"\n{json_result.novel_text}"
	return text

async def saveNovel(novelid):
	name = await getNovelInfo(novelid)
	name = name [0]
	path = os.path.join(os.getcwd(), "Novels", "async", f"{name}.txt")
	text = await getNovelText(novelid)
	await saveText(path, text)
	print(f"【{name}.txt】已保存")
	return path
	
async def getNovelsList(seriesid):
	novellist = []
	tags = set()
	json = tokenPool.getAPI().novel_series(seriesid, last_order=None)
	for novel in json.novels:
		novellist.append(novel.id)
	next_qs = tokenPool.getAPI().parse_qs(json.next_url)
	while next_qs is not None:
		json = tokenPool.getAPI().novel_series(**next_qs)
		for novel in json.novels:
			novellist.append(novel.id)
		next_qs = tokenPool.getAPI().parse_qs(json.next_url)
		
	# print(len(novellist), novellist, tags, sep="\n")
	return novellist
	
	
@timer
def saveNovelMain():
	novelid = "10506479"
	asyncio.run(saveNovel(novelid))
	
	
async def saveSeries(seriesid):
	novellist = await getNovelsList(seriesid)
	async for novelid in AsyncIterator(novellist):   #2.45s, class 1.46s
	# for novelid in novellist:   # 3.49s
		await saveNovel(novelid)
		
		
		
		
@timer
def saveSeriesMain():
	seriesid = "1530518"
	asyncio.gather(saveSeries(seriesid))
	
	
@timer
def a():
	asyncio.run(copymain())
	
@timer
def b():
	from FileOperate import readText, saveText
	path = r"D:\OneDrive - yangtzeu.edu.cn\写作\小说"
	l = findFile(path, ".txt")
	for file in l:
		# print(file)
		text = readText(file)
		path = os.path.join("..","n3",os.path.basename(file))
		# print(path)
		saveText(path, text)
		

if __name__ == '__main__':
	# saveNovelMain()
	saveSeriesMain()
	pass
	# a()
	# b()
	# main()
