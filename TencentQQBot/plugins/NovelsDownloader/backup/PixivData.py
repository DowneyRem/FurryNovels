#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import time
from datetime import date, timedelta
from functools import wraps
from platform import platform

import pandas as pd
from pixivpy3 import AppPixivAPI
from win32com.client import DispatchEx, Dispatch
from TokenRoundRobin import TokenRoundRobin
from configuration import Pixiv_Tokens

# get your refresh_token, and replace _REFRESH_TOKEN
# https://github.com/upbit/pixivpy/issues/158#issuecomment-778919084
REFRESH_TOKEN = "dF65pCDr55GmUjxwZ2FHZvFbXj59qmdIhJVfy2OqEHk",  # DowneyRrm0  Gmail
_TEST_WRITE = False
sys.dont_write_bytecode = True
tokenPool = TokenRoundRobin(Pixiv_Tokens)

if "Windows" in platform():
	import winreg
	REQUESTS_KWARGS = {'proxies': {'https': 'http://127.0.0.1:10808', }}
else:
	REQUESTS_KWARGS = {}
#
# try:
# 	tokenPool.getAAPI() = AppPixivAPI(**REQUESTS_KWARGS)
# 	tokenPool.getAAPI().auth(refresh_token=REFRESH_TOKEN)
# except:
# 	print("请检查网络可用性或更换REFRESH_TOKEN")


def timethis(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		r = func(*args, **kwargs)
		end = time.perf_counter()
		print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
		return r
	return wrapper


def openFileCheck(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		arg = args[0]
		if os.path.exists(arg):
			try:
				r = func(*args, **kwargs)
				return r
			except IOError as e:
				print("文件被占用：{}".format(arg))
		else:
			print("文件不存在：{}".format(arg))
	return wrapper


def getFileTime(path):
	time1 = os.path.getctime(path)  # 文件创建日期，返回时间戳
	time2 = os.path.getmtime(path)  # 文件最近修改时间
	time3 = os.path.getatime(path)  # 文件最近访问时间
	
	list1 = [time1, time2, time3]
	list2 = []
	for i in range(len(list1)):
		filetime = list1[i]
		filetime = time.localtime(filetime)  # 返回时间元组
		timeformat = "%Y-%m-%d %H:%M:%S %w"
		timeformat = "%Y-%m-%d"
		filetime = time.strftime(timeformat, filetime)
		list2.append(filetime)
	# print(filetime)
	return list2


def formatName(text):
	list = r'/ \ : * " < > | ?'.split(" ")
	for i in range(len(list)):
		a = list[i]
		text = text.replace(a, " ")
	return text


def getNovelInfo(novel_id):
	json_result = tokenPool.getAPI().novel_detail(novel_id)
	novel = json_result.novel
	title = novel.title
	
	date = novel.create_date[0:10]
	time = novel.create_date[11:19]
	datetime = date + " " + time
	
	bookmarks = novel.total_bookmarks
	view = novel.total_view
	comments = novel.total_comments
	return title, datetime, view, bookmarks, comments


def getIllustInfo(illust_id):
	json_result = tokenPool.getAPI().illust_detail(illust_id)
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
	json_result = tokenPool.getAPI().user_detail(user_id)
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
	
	string = "{}\n系列小说：{}篇，共计：{}篇\n插画：{}张，漫画：{}章".format(name, series, novels, illusts, manga)
	string = string.replace("None", "0")
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
		next_qs = tokenPool.getAPI().parse_qs(json_result.next_url)
		if next_qs is not None:
			json_result = tokenPool.getAPI().user_novels(**next_qs)
			novelslist = addlist(json_result)
			nextpage(json_result)
	
	novelslist = []
	json_result = tokenPool.getAPI().user_novels(user_id)
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
		next_qs = tokenPool.getAPI().parse_qs(json_result.next_url)
		if next_qs is not None:
			json_result = tokenPool.getAPI().user_novels(**next_qs)
			illustslist = addlist(json_result)
			nextpage(json_result)
	
	illustslist = []
	json_result = tokenPool.getAPI().user_illusts(user_id, "illust")
	addlist(json_result)
	nextpage(json_result)
	
	json_result = tokenPool.getAPI().user_illusts(user_id, "manga")
	addlist(json_result)
	nextpage(json_result)
	
	# print(illustslist)
	return illustslist


@timethis
def formatForCsv(user_id):
	print("\n获取Pixiv数据中……")
	text = "序号,名称,日期,点击,点赞,评论\n"  # 获取到点赞其实是收藏，而不是"赞！"
	novelslist = getNovelsList(user_id)
	illustslist = getIllustsList(user_id)
	
	for i in range(len(novelslist)):
		id = novelslist[i]
		num = len(novelslist) - i  # i从0开始，不需要加1
		(title, datetime, view, bookmarks, comments) = getNovelInfo(id)
		text += "{},{},{},{},{},{}\n".format(num, title, datetime, view, bookmarks, comments)
	
	for i in range(len(illustslist)):
		id = illustslist[i]
		num = len(novelslist) + len(illustslist) - i
		(title, datetime, view, bookmarks, comments) = getIllustInfo(id)
		text += "{},{},{},{},{},{}\n".format(num, title, datetime, view, bookmarks, comments)
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


def saveAsCsv(user_id, path):
	author = getUserInfo(user_id)[0]
	author = formatName(author)
	path = os.path.join(path, author + ".csv")
	# print(path)
	text = formatForCsv(user_id)
	saveCsv(path, text)
	return path


# @timethis
def formatForDataFrame(user_id):
	li = []
	print("\n获取Pixiv数据中……")
	novelslist = getNovelsList(user_id)
	illustslist = getIllustsList(user_id)
	
	for i in range(len(novelslist)):
		id = novelslist[i]
		(title, datetime, view, bookmarks, comments) = getNovelInfo(id)
		li.append([title, datetime, view, bookmarks, comments])
	
	for i in range(len(illustslist)):
		id = illustslist[i]
		(title, datetime, view, bookmarks, comments) = getIllustInfo(id)
		li.append([title, datetime, view, bookmarks, comments])
	return li


@timethis
def saveAsXlsx(user_id, path):
	data = formatForDataFrame(user_id)
	col = "名称,日期,点击,点赞,评论".split(",")
	df = pd.DataFrame(data, columns=col)
	df = df.sort_values(by="日期")
	df.index = range(1, len(df) + 1)
	# print(df)
	
	author = getUserInfo(user_id)[0]
	author = formatName(author)
	today = date.today()
	path = os.path.join(path, author + ".xlsx")
	# print(path)
	try:
		df.to_excel(path, sheet_name="数据", index_label=today,)
		name = os.path.split(path)[1]
		print("已存为：【{}】".format(name))
		return path
	except:
		print("保存失败")
		return None


@timethis
@openFileCheck
def openExcel(path, Visible=0):  # 打开软件手动操作
	# excel = DispatchEx('Excel.Application')  # 工作簿间独立进程
	excel = Dispatch('Excel.Application')
	excel.Visible = Visible  # 0为后台运行
	excel.DisplayAlerts = 0  # 不显示警告
	print("打开Excel……")
	excel.Workbooks.Open(path, 0)  # 打开文档


@timethis
@openFileCheck
def editExcel(path, Visible=0):  # 打开软件自动操作，需要录制宏
	extdict = {
		".xlsb": "50",  # Excel 二进制工作簿
		".xlsx": "51",  # 默认/Open XML 工作簿
		".xlsm": "52",  # 启用宏的 Open XML 工作簿
		".xltm": "53",  # 启用宏的 Open XML 模板
		".xltx": "54",  # Open XML 模板
		".xls": "56",  # Excel 97-2003 工作簿
		".csv": "62",  # UTF8 CSV
		}
	
	# excel = DispatchEx('Excel.Application')  # 工作簿间独立进程
	excel = Dispatch('Excel.Application')  # 工作簿共用进程
	excel.Visible = Visible  # 0为后台运行
	excel.DisplayAlerts = 0  # 不显示警告
	print("处理数据中……")
	wb = excel.Workbooks.Open(path, UpdateLinks=3)  # 打开文档；更新链接
	wb.Application.Run("自动化")  # 运行宏


# 保存，并另存为 xlsx
# wb.Save()
# path = os.path.splitext(path)[0] + ".xlsx"
# ext = os.path.splitext(path)[1]
# extnum = extdict.get(ext)
# wb.SaveAs(path, extnum)

# wb.Close(True)
# excel.Quit()
# return path


def desktop():
	if "Windows" in platform():  # 其他平台我也没用过
		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
				r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
		desktop = winreg.QueryValueEx(key, "Desktop")[0]
		return desktop


@timethis
def main():
	def wrong():
		print("输入错误，请重新输入")
		main()
	
	print("\n请输入Pixiv作者链接：")
	string = input()
	if re.search("[0-9]+", string):
		id = re.search("[0-9]+", string).group()
		print("开始获取作者相关数据")
		if "pixiv.net" in string and "users" in string:
			try:
				fliepath = saveAsXlsx(id, path)
			except:
				fliepath = saveAsCsv(id, path)
			openExcel(fliepath)
		else:
			print("尝试按作者ID解析")
			try:
				fliepath = saveAsXlsx(id, path)
			except:
				fliepath = saveAsCsv(id, path)
	else:
		wrong()


if __name__ == '__main__':
	def main2():
		path = os.getcwd()
		path = path.replace("写作\\小说推荐\\工具", "")
		path = os.path.join(path, "Office Documents", "WPS Cloud Files")
		xlsxpath = os.path.join(path, "唐门小说点赞统计.xlsm")
		
		fileModifyTime = os.path.getmtime(xlsxpath)
		fileModifyTime = date.fromtimestamp(fileModifyTime)
		today = date.today()
		today_wday = today.isoweekday()
		
		if today_wday >= 5 and today - fileModifyTime >= timedelta(5):
		# if True:
			datapath = saveAsXlsx(16721009, desktop())
			datapath = os.path.join(desktop(), "唐尼瑞姆 唐门.xlsx")
			openExcel(datapath, 1)
			editExcel(xlsxpath, 1)
		else:
			path = os.path.join(path, "唐门小说更新统计.xlsm")
			openExcel(path, 1)
	
	
	path = os.getcwd()
	if "Novels" not in path:
		main()
	else:
		main2()
