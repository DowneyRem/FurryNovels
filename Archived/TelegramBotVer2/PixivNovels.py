#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import math
import logging

import numpy as np

from FileOperate import zipFile, saveText, formatFileName, makeDirs
from TextFormat import formatNovelName, formatCaption, formatText
from TokenRoundRobin import TokenRoundRobin
from Translate import getLanguage
from config import Pixiv_Tokens

if "小说推荐" in os.getcwd():
	from FileOperate import saveDocx


logging.basicConfig(level=logging.INFO,
		format='%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
		datefmt='%Y.%m.%d. %H:%M:%S',
		# filename='parser_result.log',
		# filemode='w'
)

sys.dont_write_bytecode = True
_TEST_WRITE = False
tokenPool = TokenRoundRobin(Pixiv_Tokens)


def set2Text(s):
	text = " ".join(s)
	return text


def getLang(novel_id):
	text = getNovelText(novel_id)
	lang = getLanguage(text)
	return f"#{lang}"


def getTags(novel_id, set):
	# set 去重复标签，支持系列小说
	json_result = tokenPool.getAAPI().novel_detail(novel_id)
	tags = json_result.novel.tags
	for i in range(len(tags)):
		tagn = tags[i]
		# if tagn.translated_name is not None:
		# 	tag = dict.translated_name
		# 	set.add("#" + tag)
		tag = tagn.name
		set.add("#" + tag)
	return set


def getAuthorName(json):
	#账户名，id，头像图片；支持小说，小说系列，插画，漫画
	user = json.user
	id = user.id
	name = formatFileName(user.name)
	account = user.account
	return name, id


def getSeriesId(novel_id):
	try:
		json_result = tokenPool.getAAPI().novel_detail(novel_id)
		series = json_result.novel.series
		title = series.title
		id = series.id
		# print(title, id)
		return id, title
	except:
		return None, None


def getNovelInfo(novel_id):
	json_result = tokenPool.getAAPI().novel_detail(novel_id)
	# print(json_result)
	novel = json_result.novel
	title = novel.title
	author, authorid = getAuthorName(novel)
	caption = formatCaption(novel.caption)
	view = novel.total_view
	bookmarks = novel.total_bookmarks
	comments = novel.total_comments
	
	image_urls = novel.image_urls
	text_length = novel.text_length
	return title, author, caption, view, bookmarks, comments, authorid


def formatNovelInfo(novel_id, mode=0):
	(title, author, caption) = getNovelInfo(novel_id)[0:3]
	URL = f"网址：https://www.pixiv.net/novel/show.php?id={novel_id}"
	
	s = set()
	s = getTags(novel_id, s)
	s.add(getLang(novel_id))
	tags = f"标签：{set2Text(s)}"
	
	if caption != "":
		caption = f"其他：{caption}\n"
	
	if mode == 0:
		string = f"{title}\n作者：{author}\n{URL}\n{tags}\n{caption}"
	else:
		string = f"{title}\n作者：{author}\n{tags}\n{caption}{URL}"
	# print(string)
	return string


def getNovelText(novel_id):
	text = "\n"
	json_result = tokenPool.getAAPI().novel_text(novel_id)
	if json_result.novel_text:
		text += json_result.novel_text
	else:
		text += "因作者设置（或达到请求次数），无法获取小说文本"
		logging.error(text.strip())
	
	text = formatText(text)
	# print (text)
	return text


def saveNovel(novel_id, path):
	text = formatNovelInfo(novel_id)
	text += "\n" * 2
	text += getNovelText(novel_id)
	# print(text)
	
	name = formatNovelName(getNovelInfo(novel_id)[0])
	name = formatFileName(name)
	
	if "小说推荐" in path:
		filepath = os.path.join(path, name + ".docx")
		saveDocx(filepath, text)
		print("【{}.docx】已保存".format(name))
	
	else:
		filepath = os.path.join(path, name + ".txt")
		saveText(filepath, text)
		print("【{}.txt】已保存".format(name))
	
	return filepath


# 【【【【系列小说】】】】
def getNovelsListFromSeries(series_id):
	def addlist(json_result):
		novels = json_result.novels
		for i in range(len(novels)):
			id = novels[i].id
			novellist.append(id)
		# print(len(novellist))
		return novellist
	
	def nextpage(json_result):
		next_qs = tokenPool.getAAPI().parse_qs(json_result.next_url)
		if next_qs is not None:
			json_result = tokenPool.getAAPI().novel_series(**next_qs)
			novellist = addlist(json_result)
			nextpage(json_result)
	
	novellist = []
	json_result = tokenPool.getAAPI().novel_series(series_id, last_order=None)
	addlist(json_result)
	nextpage(json_result)
	return novellist


def getSeriesInfo(series_id):
	json_result = tokenPool.getAAPI().novel_series(series_id, last_order=None)
	# print(json_result)
	detail = json_result.novel_series_detail
	title = formatFileName(detail.title)  # 系列标题
	author = getAuthorName(detail)[0]
	caption = formatCaption(detail.caption)  # 系列简介
	count = detail.content_count  # 系列内小说数
	url = json_result.novels[0].image_urls.medium
	
	# name = formatFileName(title) + ".jpg"
	# tokenPool.getAAPI().download(url, path="Photos", name=name)
	# iconpath = os.path.join(os.getcwd(), "Photos", name)
	# print(title, authorname, count, caption, iconpath)
	return title, author, caption, count


def formatSeriesInfo(series_id):
	(title, author, caption, count) = getSeriesInfo(series_id)[0:4]
	author = "作者：{}\n".format(author)
	
	if caption != "":
		caption = "其他：{}\n".format(caption)  # 系列简介
	
	list = getNovelsListFromSeries(series_id)
	novel_id = list[0]
	url = "网址：https://www.pixiv.net/novel/show.php?id={}\n".format(novel_id)
	
	print("系列：{} 共有{}章".format(title, count))
	if len(list) != count:
		print("已获取{}章".format(len(list)))
	
	s = set()
	s.add(getLang(novel_id))
	for i in range(len(list)):
		id = list[i]
		s = getTags(id, s)
	tag = "标签：{}\n".format(set2Text(s))
	
	info = title + "\n" + author + url + tag + caption
	# print(info)
	return info


def getSeriesText(series_id):
	text = "\n"
	list = getNovelsListFromSeries(series_id)
	for i in range(len(list)):
		id = list[i]
		title = formatNovelName(id) + "\n"
		if ("第" not in title) and ("章" not in title):
			title = "第{}章 {}".format(i + 1, title)
		text += title
		text += getNovelText(id)
		text += "\n　　" * 3
	return text


def saveSeriesAsTxt(series_id, path):
	print("开始下载txt合集")
	text = formatSeriesInfo(series_id) + "\n" * 2
	text += getSeriesText(series_id)
	
	name = getSeriesInfo(series_id)[0]
	name = formatFileName(name)
	
	if "小说推荐" in path:
		filepath = os.path.join(path, name + ".docx")
		saveDocx(filepath, text)
		print("【{}.docx】已保存".format(name))
	
	else:
		filepath = os.path.join(path, name + ".txt")
		saveText(filepath, text)
		print("【{}.txt】已保存".format(name))
	
	return filepath


def saveSeriesAsZip(series_id, path):
	print("开始下载zip合集")
	dirname = getSeriesInfo(series_id)[0]
	dirname = formatFileName(dirname)
	path = os.path.join(path, dirname)
	makeDirs(path)
	
	list = getNovelsListFromSeries(series_id)
	for i in range(len(list)):
		id = list[i]
		saveNovel(id, path)
	
	zippath = zipFile(path)
	return zippath


def saveSeries(series_id, path):
	# 判断系列为一篇小说还是多篇
	def test1(series_id, novel_id, num):
		seriesName = getSeriesInfo(series_id)[0]
		seriesName = seriesName.replace("系列", "")
		novelsName = getNovelInfo(novel_id)[0]
		novelsCaption = getNovelInfo(novel_id)[2]
		
		pat1 = "(第|\(|（|-)?"
		pat2 = "(部|卷|章|节|節|篇|话|話|\)|）|-|\.)"
		
		if re.findall(pat1 + "[0-9.]+" + pat2, novelsName):
			num += 1
		elif re.findall(pat1 + "[零〇一二三四五六七八九点十百千万亿萬億]+" + pat2, novelsName):
			num += 1
		elif re.findall("[上中下]" + pat2, novelsName):
			num += 1
		elif re.findall("(设定|設定|背景|引|序章|终章|終章|番外|后记|後記)", novelsName):
			num += 1
		elif re.findall("(部|卷|章|节|節|篇|话|話)", novelsName):
			num += 1
		# elif seriesName != "" and seriesName in novelsName:
		# 	num += 1
		# print(novelsName, num)
		return num
	
	def getnum(series_id):
		list = getNovelsListFromSeries(series_id)
		count = len(list)
		
		seriesName = getSeriesInfo(series_id)[0]
		seriesCaption = getSeriesInfo(series_id)[2]
		seriesName = seriesName.replace("系列", "")
		
		if "委托" in seriesName or "委托" in seriesCaption:
			return count-100
		else:
			num = 0
			for i in range(len(list)):
				id = list[i]
				name = getNovelInfo(id)[0]
				caption = getNovelInfo(id)[2]
				
				if re.findall("(?:给|給)?.+?的?(?:委托|赠文|无偿)", name):
					num = -100
					break
				elif re.findall("(?:给|給)?.+?的?(?:委托|赠文|无偿)", caption):
					num = -100
					break
				else:
					num = test1(series_id, id, num)
			
			num = 100 * num / count
			return num
	
	num = getnum(series_id)
	# print(num)
	if num > +60:
		filepath = saveSeriesAsTxt(series_id, path)
	if num < -60:
		filepath = saveSeriesAsZip(series_id, path)
	else:
		filepath = saveSeriesAsTxt(series_id, path)
		filepath = saveSeriesAsZip(series_id, path)
	return filepath


# 【【【用户页面】】】
def getAuthorInfo(user_id):
	string = ""
	json_result = tokenPool.getAAPI().user_detail(user_id)
	# print(json_result)
	user = json_result.user
	id = user.id
	name = formatFileName(user.name)
	account = user.account
	url = user.profile_image_urls.medium
	comment = formatCaption(user.comment)
	
	profile = json_result.profile
	webpage = profile.webpage
	twitter = profile.twitter_url
	
	illusts = profile.total_illusts
	manga = profile.total_manga
	iseries = profile.total_illust_series
	novels = profile.total_novels
	nseries = profile.total_novel_series
	string = "{}({})\n小说：{}篇；系列：{}个\n插画：{}幅；系列：{}个"\
		.format(name, id, novels, nseries, illusts+manga, iseries)
	# print(string)
	
	makeDirs(os.path.join(".", "Photos"))
	name = formatFileName(name) + ".jpg"
	tokenPool.getAAPI().download(url, path="Photos", name=name)
	iconpath = os.path.join(os.getcwd(), "Photos", name)
	
	# return name, id, novels, nseries, illusts+manga, iseries, iconpath
	return string, iconpath


def getNovelsListFromAuthor(user_id):
	def addlist(json_result):
		novels = json_result.novels
		for i in range(len(novels)):
			id = novels[i].id
			novelslist.append(id)
		# print(len(novelslist))
		return novelslist
	
	def nextpage(json_result):
		next_qs = tokenPool.getAAPI().parse_qs(json_result.next_url)
		if next_qs is not None:
			json_result = tokenPool.getAAPI().user_novels(**next_qs)
			novelslist = addlist(json_result)
			nextpage(json_result)
	
	novelslist = []
	json_result = tokenPool.getAAPI().user_novels(user_id)
	addlist(json_result)
	nextpage(json_result)
	return novelslist


def getSeriesList(novellist):
	s = set()
	for i in range(len(novellist)):
		novel_id = novellist[i]
		series_id = getSeriesId(novel_id)[0]
		if series_id is not None:
			s.add(series_id)
	serieslist = list(s)
	# print(len(serieslist), serieslist, sep="\n")
	return serieslist


def saveAuthor(user_id, path):
	novelslist = getNovelsListFromAuthor(user_id)
	serieslist = getSeriesList(novelslist)
	
	novel_id = novelslist[0]
	author = getNovelInfo(novel_id)[1]
	author = formatFileName(author)
	path = os.path.join(path, author)
	print("保存目录：" + path)
	
	for i in range(len(novelslist)):
		novel_id = novelslist[i]
		series_id = getSeriesId(novel_id)[0]
		if series_id is None:
			saveNovel(novel_id, path)
	
	for i in range(len(serieslist)):
		series_id = serieslist[i]
		saveSeriesAsTxt(series_id, path)
	
	zippath = zipFile(path)
	return zippath


# 【【【【数据统计部分】】】】
def novelAnalyse(novel_id):
	(view, bookmarks, comments) = getNovelInfo(novel_id)[3:6]
	rate = 100 * bookmarks / view
	# print(view, bookmarks, comments, round(rate, 2))
	recommend = 0  # 推荐指数
	
	if comments >= 1:  # 根据评论量增加推荐指数
		i = math.log2(comments)
		recommend += round(i, 2)
	# print(round(i, 2))
	
	if view >= 0:  # 根据阅读量和收藏率增加推荐指数
		numlist = []; a = -7.75; step1 = 1; step2 = 0.75
		for a in np.arange(a, a + 9 * step1, step1):  # 生成首列数据
			b = np.arange(a, a + 21 * step2, step2)  # 生成首行数据
			numlist.append(list(b))
		numlist = np.asarray(numlist)
		# print(numlist)
		
		x = int(view // 500)
		y = int(rate // 0.5)
		if x >= len(numlist):
			x = len(numlist) - 1
		if y >= len(numlist[0]):
			y = len(numlist[0]) - 1
		recommend += numlist[x, y]
	# print(numlist[x,y])
	
	if view <= 1000:  # 对阅读量小于1000的小说适当提高要求
		recommend += -0.75
	
	print("推荐指数：{:.2f}".format(recommend))
	return recommend


def seriesAnalyse(series_id):
	novel_id = getNovelsListFromSeries(series_id)[0]
	recommend = novelAnalyse(novel_id)  # 系列取第一篇进行统计
	return recommend


def analyse(id):
	def testAnalyse(novel_id):
		if getSeriesId(novel_id)[0] is None:
			recommend = novelAnalyse(novel_id)
		else:
			series_id = getSeriesId(novel_id)[0]
			recommend = seriesAnalyse(series_id)
		return recommend
	
	try:
		novellist = getNovelsListFromSeries(id)
		id = novellist[0]
		recommend = seriesAnalyse(id)
	except TypeError:  # 非系列id报错
		recommend = testAnalyse(id)
	return recommend


# 【【【主函数部分】】】】
def main():
	def wrong():
		print("输入有误，请重新输入")
		main()
	
	def testSeries(novel_id):
		analyse(novel_id)
		if getSeriesId(novel_id)[0] is None:
			print("开始下载单篇小说……")
			saveNovel(novel_id, path)
		else:
			series_id = getSeriesId(novel_id)[0]
			saveSeries(series_id, path)
	
	def download(string, id):
		if "novel/series" in string:
			print("开始下载系列小说……")
			analyse(id)
			saveSeriesAsZip(id, path)
		# saveSeries(id, path)
		elif "novel" in string:
			testSeries(id)
		elif "users" in string:
			print("开始下载此作者的全部小说")
			getAuthorInfo(id)
			saveAuthor(id, path)
		elif "artworks" in string:
			print("不支持下载插画，请重新输入")
	
	
	print("\n请输入Pixiv小说链接")
	string = input()
	if re.search("[0-9]{5,}", string):
		id = re.search("[0-9]{5,}", string).group()
		if "pixiv.net" in string:
			download(string, id)
		else:
			testSeries(id)
		main()
	else:
		wrong()


if __name__ == '__main__':
	# path = os.getcwd()
	# if "小说推荐" in path:
	# 	path = path.replace("\\工具", "")
	# 	path = os.path.join(path, "备用")
	# else:
	# 	path = os.path.join(os.getcwd(), "Photos")
	# 	makeDirs(path)
	# 	path = os.path.join(os.getcwd(), "Novels")
	# 	makeDirs(path)
	# main()
	
	
	a = getNovelInfo(11775832)[2]
	print(a)