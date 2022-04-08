#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
from functools import wraps
from platform import platform
from pixivpy3 import AppPixivAPI
from win32com.client import DispatchEx


# get your refresh_token, and replace _REFRESH_TOKEN
# https://github.com/upbit/pixivpy/issues/158#issuecomment-778919084
REFRESH_TOKEN = "0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4"
_TEST_WRITE = False
sys.dont_write_bytecode = True


if "Windows" in platform():
	REQUESTS_KWARGS = {'proxies':{'https':'http://127.0.0.1:10808', }}
try:
	aapi = AppPixivAPI(**REQUESTS_KWARGS)
	aapi.auth(refresh_token=REFRESH_TOKEN)
except:
	print("请检查网络可用性或更换REFRESH_TOKEN")


def timethis(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		r = func(*args, **kwargs)
		end = time.perf_counter()
		print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
		return r
	return wrapper


def getNovelInfo(novel_id):
	json_result = aapi.novel_detail(novel_id)
	novel = json_result.novel
	title = novel.title

	date = novel.create_date[0:10]
	time = novel.create_date[11:19]
	datetime = date+ " "+ time
	
	bookmarks = novel.total_bookmarks
	view = novel.total_view
	comments = novel.total_comments
	return title, datetime, view, bookmarks, comments


def getIllustInfo(illust_id):
	json_result = aapi.illust_detail(illust_id)
	illust = json_result.illust
	title = illust.title
	
	date = illust.create_date[0:10]
	time = illust.create_date[11:19]
	datetime = date + " " + time
	
	view = illust.total_view
	bookmarks = illust.total_bookmarks
	comments = illust.total_comments
	return title, datetime, view, bookmarks, comments
	

def getUserInfo(user_id):
	string = ""
	json_result = aapi.user_detail(user_id)
	# print(json_result)
	user = json_result.user
	id = user.id
	name = user.name
	account = user.account
	profile_image_urls = user.profile_image_urls.medium
	comment = user.comment
	
	profile = json_result.profile
	webpage = profile.webpage
	twitter = profile.twitter_url
	total_follow_users = profile.total_follow_users
 
	novels = profile.total_novels
	series = profile.total_novel_series
	illusts = profile.total_illusts
	manga = profile.total_manga
 
	string = "{}\n系列小说：{}篇，共计：{}篇\n插画：{}张，漫画：{}章".format(name, series, novels, illusts, manga )
	print(string)
	return name, novels, series, illusts, manga
	

def getNovelsList(user_id):
	def addlist(json_result):
		novels = json_result.novels
		for i in range(len(novels)):
			id = novels[i].id
			novelslist.append(id)
		# print(len(novelslist))
		return novelslist
	
	def nextpage(json_result):
		next_qs = aapi.parse_qs(json_result.next_url)
		if next_qs is not None:
			json_result = aapi.user_novels(**next_qs)
			novelslist = addlist(json_result)
			nextpage(json_result)
	
	novelslist = []
	json_result = aapi.user_novels(user_id)
	addlist(json_result)
	nextpage(json_result)
	return novelslist


def getIllustsList(user_id):
	def addlist(json_result):
		illusts = json_result.illusts
		for i in range(len(illusts)):
			id = illusts[i].id
			illustslist.append(id)
		# print(len(illustslist))
		return illustslist
	
	def nextpage(json_result):
		next_qs = aapi.parse_qs(json_result.next_url)
		if next_qs is not None:
			json_result = aapi.user_novels(**next_qs)
			illustslist = addlist(json_result)
			nextpage(json_result)
	
	illustslist = []
	json_result = aapi.user_illusts(user_id, "illust")
	addlist(json_result)
	nextpage(json_result)
	json_result = aapi.user_illusts(user_id, "manga")
	addlist(json_result)
	nextpage(json_result)
	# print(illustslist)
	return illustslist


@timethis
def formatData(user_id):
	print("\n获取Pixiv数据中……")
	text = "序号,名称,日期,点击,点赞,评论\n"  #获取到点赞其实是收藏，而不是"赞！"
	novelslist = getNovelsList(user_id)
	illustslist = getIllustsList(user_id)
	
	for i in range(len(novelslist)):
		id = novelslist[i]
		num = len(novelslist) - i  ## i从0开始，不需要加1
		(title, datetime, view, bookmarks, comments) = getNovelInfo(id)
		text += "{},{},{},{},{},{}\n".format(num, title ,datetime , view, bookmarks, comments)
		
	for i in range(len(illustslist)):
		id = illustslist[i]
		num = len(novelslist) + i
		(title, datetime, view, bookmarks, comments) = getIllustInfo(id)
		text += "{},{},{},{},{},{}\n".format(num, title ,datetime , view, bookmarks, comments)
		
	return text


def saveCsv(path, text):
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	if not os.path.exists(dir):
		os.makedirs(dir)
	try:
		with open(path, "w", encoding="UTF-8-sig") as f:
			f.write(text)
		print("已存为：" + name)
	except IOError:
		print("保存失败")


def formatName(text):
	list = '/ \ : * " < > |'.split(" ")
	for i in range(len(list)):
		a = list[i]
		text = text.replace(a, " ")
	return text


def SaveAsCsv(user_id, path):
	authro = getUserInfo(user_id)[0]
	authro = formatName(authro)
	path = os.path.join(path, authro + ".csv")
	# print(path)
	text = formatData(user_id)
	saveCsv(path, text)
	return path


# @timethis
def openExcel(path):
	try:
		excel = DispatchEx('Excel.Application')  # 独立进程
		excel.Visible = 1  # 0为后台运行
		excel.DisplayAlerts = 0  # 不显示，不警告
		xlsx = excel.Workbooks.Open(path)  # 打开文档
		print("打开Excel……")
	except:
		print("文件打开失败")


def wrong():
	print("输入错误，请重新输入")
	main()


# @timethis
def main():
	print("\n请输入Pixiv作者链接：")
	string = input()
	if re.search("[0-9]+", string):
		id = re.search("[0-9]+", string).group()
		if "pixiv.net" in string and "users" in string:
			print("开始获取作者相关数据")
			fliepath = SaveAsCsv(id, path)
			# openExcel(fliepath)
			# main()
		else:
			wrong()
	else:
		wrong()


if __name__ == '__main__':
	path = os.getcwd()
	main()

	# path = "D:\\Users\\Administrator\\Desktop"
	# path2 = "D:\\OneDrive - yangtzeu.edu.cn\\Office Documents\\WPS Cloud Files\\唐门小说点赞统计.xlsx"
	# path1 = SaveAsCsv(16721009, path)
	# openExcel(path1)
	# openExcel(path2)
