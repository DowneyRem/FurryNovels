#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import math
import numpy as np
from pixivpy3 import AppPixivAPI
from platform import platform
from FileOperate import zipFile, saveText
from config import REFRESH_TOKEN


sys.dont_write_bytecode = True
_TEST_WRITE = False


if "Windows" in platform():
	REQUESTS_KWARGS = {'proxies':{'https':'http://127.0.0.1:10808', }}
elif "Linux" in platform():
	REQUESTS_KWARGS = {}
try:
	aapi = AppPixivAPI(**REQUESTS_KWARGS)
	aapi.auth(refresh_token=REFRESH_TOKEN)
except:
	print("请检查网络可用性或更换REFRESH_TOKEN")


def set2Text(set):
	text = str(set)
	text = text.replace("{'", "")
	text = text.replace("'}", "")
	text = text.replace("', '", " ")
	return text


def formatName(text):
	list = '/ \ : * " < > | ?'.split(" ")
	for i in range(len(list)):
		a = list[i]
		text = text.replace(a, " ")
	return text


def getTags(novel_id, set):
	#set 去重复标签，支持系列小说
	json_result = aapi.novel_detail(novel_id)
	tags = json_result.novel.tags
	for i in range(len(tags)):
		dict = tags[i]
		# if dict.translated_name is not None:
		# 	tag = dict.translated_name
		# 	set.add("#"+tag)
		tag = dict.name
		set.add("#"+tag)
	return set


def getAuthorName(novel):
	#作者 昵称，id，账户，头像图片链接
	name = novel.user.name
	id = novel.user.id
	account =  novel.user.account
	profile_image_urls = novel.user.profile_image_urls.medium
	return name, id


def getSeriesId(novel_id):
	try:
		json_result = aapi.novel_detail(novel_id)
		series = json_result.novel.series
		title = series.title
		id = series.id
		# print(title, id)
		return id, title
	except:
		return None, None

	
def getNovelInfo(novel_id):
	json_result = aapi.novel_detail(novel_id)
	novel = json_result.novel
	title = novel.title
	author = getAuthorName(novel)[0]
	caption = novel.caption
	view = novel.total_view
	bookmarks = novel.total_bookmarks
	comments = novel.total_comments
	
	image_urls = novel.image_urls
	text_length = novel.text_length
	return title, author, caption, view, bookmarks, comments


def formatCaption(caption):
	# pattern = r'<a href="pixiv://(illusts|novels|users)/[0-9]{5,}">(illust|novel|user)/[0-9]{5,}</a>'
	# 不清楚为什么用完整的表达式反而会匹配不了，不得已拆成了3份
	
	#<a href="pixiv://illusts/12345">illust/12345</a>
	pattern = '<a href="pixiv://illusts/[0-9]{5,}">illust/[0-9]{5,}</a>'
	a = re.findall(pattern, caption)
	for i in range(len(a)):
		string = a[i]
		# print(string)
		id = re.search("[0-9]{5,}", string).group()
		link = "https://www.pixiv.net/artworks/{}".format(id)
		caption = caption.replace(string, link)
		
	#<a href="pixiv://novels/12345">novel/12345</a>
	pattern = '<a href="pixiv://novels/[0-9]{5,}">novel/[0-9]{5,}</a>'
	a = re.findall(pattern, caption)
	for i in range(len(a)):
		string = a[i]
		id = re.search("[0-9]{5,}", string).group()
		link = "https://www.pixiv.net/novel/show.php?id={}".format(id)
		caption = caption.replace(string, link)
	
	#<a href="pixiv://users/12345">user/12345</a>
	pattern = '<a href="pixiv://users/[0-9]{5,}">user/[0-9]{5,}</a>'
	a = re.findall(pattern, caption)
	for i in range(len(a)):
		string = a[i]
		id = re.search("[0-9]{5,}", string).group()
		link = "https://www.pixiv.net/users/{}".format(id)
		caption = caption.replace(string, link)
	return caption


def formatNovelInfo(novel_id):
	(title, author, caption) = getNovelInfo(novel_id)[0:3]
	title = title + "\n"
	author = "作者：{}\n".format(author)
	URL = "网址：https://www.pixiv.net/novel/show.php?id={}\n".format(novel_id)
	
	s = set()
	tags = set2Text(getTags(novel_id, s))
	tags = "标签：" + tags+ "\n"
	
	if caption != "":
		caption = "其他：{}\n".format(caption)
		caption = caption.replace("<br />", "\n")
		caption = caption.replace("<strong>", "")
		caption = caption.replace("</strong>", "")
		caption = formatCaption(caption)
		
	string = title + author + URL + tags + caption
	print(string)
	return string


def formatNovelText(text):
	text = text.replace(" ", "")
	text = re.sub("\.{3,}", "……", text)  #省略号标准化
	text = re.sub("。。。{3,}", "……", text)
	
	text = re.sub("\n{2,}", "\n\n", text)
	text = re.sub("\n {1,}", "\n　　", text) #半角空格换成全角空格
	if "　　" not in text:  # 直接添加全角空格
		text = text.replace("\n", "\n　　")
	return text
	
	
def formatPixivText(text, novel_id):
	##处理Pixiv 标识符
	# [newpage]  [chapter: 本章标题]
	text = text.replace("[newpage]","\n\n")
	a = re.findall("\[chapter:(.*)\]", text)
	for i in range(len(a)):
		string = a[i]
		if "第" in string and "章" in string:
			string = string.replace("章", "节")
		elif re.search("[0-9]+", string):
			string = "第{}节".format(string)
		elif re.search("[二三四五六七八九]?[十]?[一二三四五六七八九十]", string):
			string = "第{}节".format(string)
		else:
			string = "第{}节 {}".format(i+1, string)
		text = re.sub("\[chapter:(.*)\]", string, text, 1)
	
	# [jump: 链接目标的页面编号]
	a = re.findall("\[jump:(.*)\]", text)
	for i in range(len(a)):
		string = a[i]
		string = "跳转至第{}节".format(string)
		text = re.sub("\[jump:(.*)\]", string, text, 1)

	# [pixivimage: 作品ID]
	a = re.findall("\[pixivimage:(.*)\]", text)
	for i in range(len(a)):
		string = a[i]
		string = "插图：https://www.pixiv.net/artworks/".format(string)
		text = re.sub("\[pixivimage:(.*)\]", string, text, 1)
		
	# [[jumpuri: 标题 > 链接目标的URL]]
	a = re.findall("\[{2}jumpuri: *(.*) *> *(.*)\]{2}", text)
	for i in range(len(a)):
		name = a[i][0]
		link = a[i][1]
		if link in name:
			text = re.sub("\[{2}jumpuri: *(.*) *> *(.*)\]{2}", link, text, 1)
		else:
			string = "{}【{}】".format(name, link)
			text = re.sub("\[{2}jumpuri: *(.*) *> *(.*)\]{2}", string, text, 1)
	
	# [uploadedimage: 上传图片自动生成的ID]
	# 会被 pixivpy 自动转换成一下这一大串
	stringpart ="jumpuri:If you would like to view illustrations, please use your desktop browser.>https://www.pixiv.net/n/"
	autostring = "[[{}{}]]".format(stringpart, novel_id)
	text = text.replace(autostring, "【此文内有插图，请在Pixv查看】")
	return text


def getNovelText(novel_id):
	text = "\n"
	json_result = aapi.novel_text(novel_id)
	text += json_result.novel_text
	series_prev = json_result.series_prev
	series_next = json_result.series_next
	
	text = formatNovelText(text)
	text = formatPixivText(text, novel_id)
	# print (text)
	return text


def saveNovel(novel_id, path):
	name = getNovelInfo(novel_id)[0]
	name = formatName(name)
	filepath = os.path.join(path, name + ".txt")

	text = formatNovelInfo(novel_id)
	text += "\n" * 2
	text += getNovelText(novel_id)
	# print(text)
	saveText(filepath, text)
	print("【" + name + ".txt】已保存")
	return filepath
	

### 【【【【系列小说】】】】
def getNovelsListFormSeries(series_id):
	def addlist(json_result):
		novels = json_result.novels
		for i in range(len(novels)):
			id = novels[i].id
			novellist.append(id)
		# print(len(novellist))
		return novellist
	
	def nextpage(json_result):
		next_qs = aapi.parse_qs(json_result.next_url)
		if next_qs is not None:
			json_result = aapi.novel_series(**next_qs)
			novellist = addlist(json_result)
			nextpage(json_result)
		
	novellist = []
	json_result = aapi.novel_series(series_id, last_order=None)
	addlist(json_result)
	nextpage(json_result)
	return novellist
	
	
def getSeriesInfo(series_id):
	json_result = aapi.novel_series(series_id, last_order=None)
	detail = json_result.novel_series_detail
	title = detail.title   #系列标题
	author = getAuthorName(detail)[0]
	caption = detail.caption  # 系列简介
	count = detail.content_count  # 系列内小说数
	# print(title, author, count, caption)
	return title, author, caption, count

	
def formatSeriesInfo(series_id):
	(title, author, caption, content_count) = getSeriesInfo(series_id)
	info = "" ; s = set()
	author = "作者：{}\n".format(author)
	info += title +"\n"+ author
	if caption != "":
		caption = "其他：{}\n".format(caption)    #系列简介
		caption = caption.replace("\n\n", "\n")
		caption = caption.replace("", "")

	list = getNovelsListFormSeries(series_id)
	print("系列：{} 共有{}章".format(title, content_count))
	if len(list) != content_count:
		print("已获取{}章".format(len(list)))
	
	for i in range(len(list)):
		id = list[i]
		s = getTags(id, s)
	
	url = "https://www.pixiv.net/novel/show.php?id={}".format(list[0])
	info += "网址：{}\n".format(url)
	info += "标签：{}\n".format(set2Text(s))
	info += caption + "\n"*2
	# print(info)
	return info

	
def getSeriesText(series_id):
	text = "\n"
	list = getNovelsListFormSeries(series_id)
	for i in range(len(list)):
		id = list[i]
		title = getNovelInfo(id)[0] + "\n"
		if ("第"not in title) and ("章" not in title):
			title = "第{}章 {}".format(i+1, title)
		text += title
		text += getNovelText(id)
		text += "\n　　" * 3
	return text


def saveSeries(series_id, path):
	name = getSeriesInfo(series_id)[0]
	name = formatName(name)
	filepath = os.path.join(path, name + ".txt")

	text = formatSeriesInfo(series_id)
	text += getSeriesText(series_id)
	saveText(filepath, text)
	print("【{}.txt】已保存".format(name))
	return filepath


### 【【【用户页面】】】
def getAuthorInfo(user_id):
	string = ""
	json_result = aapi.user_detail(user_id)
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
	total_illusts = profile.total_illusts
	total_manga = profile.total_manga
	
	total_novels = profile.total_novels
	total_series = profile.total_novel_series
	string = "{}({})\n系列小说：{}篇\n共计：{}篇".format(name, id, total_series, total_novels)
	
	# print(string)
	return string
	# return name, total_novels, total_series
	
	
def getNovelsListFromAuthor(user_id):
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


def getSeriesList(novellist):
	s= set()
	for i in range(len(novellist)):
		novel_id = novellist[i]
		series_id = getSeriesId(novel_id)[0]
		if series_id is not None:
			s.add(series_id)
	serieslist = list(s)
	# print(serieslist)
	return serieslist
 

def saveAuthor(user_id, path):
	novelslist = getNovelsListFromAuthor(user_id)
	serieslist = getSeriesList(novelslist)
	
	novel_id = novelslist[0]
	author = getNovelInfo(novel_id)[1]
	author = formatName(author)
	path = os.path.join(path, author)
	print("保存目录：" + path)
	
	for i in range(len(novelslist)):
		novel_id = novelslist[i]
		series_id = getSeriesId(novel_id)[0]
		if series_id is None:
			saveNovel(novel_id, path)
		
	for i in range(len(serieslist)):
		series_id = serieslist[i]
		saveSeries(series_id, path)
	zippath = zipFile(path)
	return zippath


def testSeries(id):
	# saveNovel(id, path)
	if getSeriesId(id)[0] is None:
		print("开始下载单篇小说……")
		saveNovel(id, path)
	else:
		print("该小说为系列小说")
		print("开始下载系列小说……")
		id = getSeriesId(id)[0]
		saveSeries(id, path)


def wrongType():
	print("输入有误，请重新输入")
	main()


def main():
	print("\n请输入Pixiv小说链接")
	string = input()
	if re.search("[0-9]+", string):
		id = re.search("[0-9]+", string).group()
		if "pixiv.net" in string:
			if "novel/series" in string:
				print("开始下载系列小说……")
				saveSeries(id, path)
				main()
			elif "novel" in string:
				analyse(id)
				testSeries(id)
				main()
			elif "users" in string:
				print("开始下载此作者的全部小说")
				getAuthorInfo(id)
				saveAuthor(id, path)
				main()
			elif "artworks" in string:
				print("不支持下载插画，请重新输入")
				main()
		elif re.search("[0-9]+", string):
			id = re.search("[0-9]+", string).group()
			if len(id) >= 5:
				print("检测到纯数字，按照小说id解析")
				testSeries(id)
			else:
				wrongType()
		else:
			wrongType()
	else:
		wrongType()


def analyse(novel_id):
	(view, bookmarks, comments) = getNovelInfo(novel_id)[3:6]
	rate = 100 * bookmarks / view
	recommend = 0   # 推荐指数
	
	if comments >= 1: # 根据评论量增加推荐指数
		i = math.log2(comments)
		recommend += round(i, 1)
		# print(round(i, 1))

	if view >= 0:  # 根据阅读量和收藏率增加推荐指数
		a = -5 ; numlist = []
		while a <= 3:
			b = np.arange(a, a+10, 1)
			b = list(b)
			numlist += b
			a += 1
		# 以2000+点击量，5%收藏率为准入门槛，设置为3
		numlist = np.asarray([numlist])
		numlist = numlist.reshape(9, 10)
		# print(numlist)
		
		x = view // 500
		y = int(rate // 1) - 1
		if x >= 9:
			x = 8
		if y >= 10:
			y = 9
		recommend += numlist[x,y] + y/2
		# print(numlist[x,y], y/2)
	
	print("推荐指数：{}".format(recommend))
	return recommend


if __name__ == '__main__':
	path = os.getcwd()
	path = os.path.join(path, "Novels")
	main()


