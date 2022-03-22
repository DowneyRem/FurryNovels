#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
from pixivpy3 import AppPixivAPI
from FileOperate import zipFile, saveText #, saveDocx


sys.dont_write_bytecode = True

# get your refresh_token, and replace _REFRESH_TOKEN
# https://github.com/upbit/pixivpy/issues/158#issuecomment-778919084
_REFRESH_TOKEN = "0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4"
_TEST_WRITE = False

# If a special network environment is meet, please configure requests as you need.
# Otherwise, just keep it empty.
_REQUESTS_KWARGS = {
	'proxies': {
		'https': 'http://127.0.0.1:10808',
	},
	# 'verify': False,
	# PAPI use https, an easy way is disable requests SSL verify
}


aapi = AppPixivAPI(**_REQUESTS_KWARGS)
aapi.auth(refresh_token=_REFRESH_TOKEN)


def set2Text(set):
	text = str(set)
	text = text.replace("{'", "")
	text = text.replace("'}", "")
	text = text.replace("', '", " ")
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


def getUserName(novel):
	#作者 昵称，id，账户，头像图片链接
	name = novel.user.name
	id = novel.user.id
	account =  novel.user.account
	profile_image_urls = novel.user.profile_image_urls.medium
	return name, id


def getSeriesFromNovel(novel_id):
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
	author = getUserName(novel)[0]
	caption = novel.caption
	
	image_urls = novel.image_urls
	text_length = novel.text_length
	total_bookmarks = novel.total_bookmarks
	total_view = novel.total_view
	total_comments = novel.total_comments
	
	return title, author, caption


def formatNovelInfo(novel_id):
	s = set()
	json_result = aapi.novel_detail(novel_id)
	novel = json_result.novel
	title = novel.title + "\n"
	authro = "作者："+ getUserName(novel)[0] + "\n"
	URL = "网址：https://www.pixiv.net/novel/show.php?id=" + str(novel_id) +"\n"
	tags = set2Text(getTags(novel_id, s))
	tags = "标签：" + tags+ "\n"
	
	caption = novel.caption
	if caption != "":
		caption = "其他：" + caption +"\n"
		caption = caption.replace("<br />", " //")
		
	string = title + authro + URL + tags + caption
	# print(string)
	return string


def getNovelText(novel_id):
	json_result = aapi.novel_text(novel_id)
	text = json_result.novel_text
	series_prev = json_result.series_prev
	series_next = json_result.series_next
	
	# text = text.replace("\n\n","\n")
	if "　"not in text:  #添加全角空格
		text = text.replace("\n","\n　　")
	# print(text)
	return text


def saveNovel(novel_id, path):
	text = formatNovelInfo(novel_id)
	text += "\n"*2
	text += getNovelText(novel_id)
	# print(text)
	name = text.split("\n")[0]
	
	try:
		path = os.path.join(path, name + ".docx")
		saveDocx(path, text)
		print("【" + name + ".docx】已保存")
	except NameError:
		path = path.replace(".docx", ".txt")
		if not os.path.exists(path):
			saveText(path, text)
		print("【" + name + ".txt】已保存")
		

### 【【【【系列小说】】】】
def getNovelIdFormSeries(series_id):
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
	authro = getUserName(detail)[0]
	caption = detail.caption  # 系列简介
	content_count = detail.content_count  # 系列内小说数
	# print(title, authro, content_count, caption)
	return title, authro, caption, content_count

	
def formatSeriesInfo(series_id):
	(title, authro, caption, content_count) = getSeriesInfo(series_id)
	info = "" ; s = set()
	authro = "作者：" + authro + "\n"
	info += title +"\n"+ authro
	if caption != "":
		caption = "其他：" + caption +"\n" #系列简介
		caption = caption.replace("\n\n", "\n")
		caption = caption.replace("", "")

	list = getNovelIdFormSeries(series_id)
	print("系列：" + title + " 共有" + str(content_count) + "章")
	if len(list) != content_count:
		print("已获取"+ str(len(list)) + "章")
	
	for i in range(len(list)):
		id = list[i]
		s = getTags(id, s)
	
	url = "https://www.pixiv.net/novel/show.php?id=" + str(list[0])
	info += "网址：" + url +"\n"
	info += "标签：" + set2Text(s)+"\n"
	info += caption + "\n"*2
	# print(info)
	return info

	
def getSeriesText(series_id):
	text = "\n"
	list = getNovelIdFormSeries(series_id)
	for i in range(len(list)):
		id = list[i]
		title = getNovelInfo(id)[0] + "\n"
		if ("第"not in title) and ("章" not in title):
			title = "第"+ str(i) + "章 "+ title
		text += title
		text += getNovelText(id)
		text += "\n" * 4
	
	# text = text.replace("\n\n","\n")
	if "　"not in text:  #添加全角空格
		text = text.replace("\n","\n　　")
	# print(text)
	return text


def saveSeries(series_id, path):
	name = getSeriesInfo(series_id)[0]
	text = formatSeriesInfo(series_id)
	text += getSeriesText(series_id)
	
	try:
		path = os.path.join(path, name + ".docx")
		saveDocx(path, text)
		print("【" + name + ".docx】已保存")
	except NameError:
		path = path.replace(".docx", ".txt")
		# print(path)
		if not os.path.exists(path):
			saveText(path, text)
		print("【" + name + ".txt】已保存")



### 【【【用户页面】】】
def getUserInfo(user_id):
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
	string = name +"\n系列小说："+str(total_series)+"篇\n共计："+str(total_novels)+"篇"
	print(string)
	return name, total_novels, total_series
	
	
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


def getSeriesList(novellist):
	s= set()
	for i in range(len(novellist)):
		novel_id = novellist[i]
		series_id = getSeriesFromNovel(novel_id)[0]
		if series_id is not None:
			s.add(series_id)
	serieslist = list(s)
	# print(serieslist)
	return serieslist
 

def saveAll(user_id, path):
	novelslist = getNovelsList(user_id)
	serieslist = getSeriesList(novelslist)
	
	novel_id = novelslist[0]
	authro = getNovelInfo(novel_id)[1]
	path = os.path.join(path, authro)
	print("保存目录：" + path)
	
	for i in range(len(novelslist)):
		novel_id = novelslist[i]
		series_id = getSeriesFromNovel(novel_id)[0]
		if series_id is None:
			saveNovel(novel_id, path)
			
	for i in range(len(serieslist)):
		series_id = serieslist[i]
		saveSeries(series_id, path)
	zipFile(path)


def testSeries(id):
	if getSeriesFromNovel(id)[0] is None:
		print("开始下载单篇小说……")
		print("")
		saveNovel(id, path)
	else:
		print("该小说为系列小说")
		print("开始下载系列小说……")
		print("")
		id = getSeriesFromNovel(id)[0]
		saveSeries(id, path)


def wrongType():
	print("输入有误，请重新输入")
	print("")
	main()
	
	
def main():
	print("请输入Pixiv小说链接")
	string = input()
	if re.search("[0-9]+", string):
		id = re.search("[0-9]+", string).group()
		if "pixiv.net" in string:
			if "novel/series" in string:
				print("开始下载系列小说……")
				print("")
				saveSeries(id, path)
			elif "novel" in string:
				testSeries(id)
			elif "users" in string:
				print("开始下载此作者的全部小说")
				getUserInfo(id)
				saveAll(id, path)
			elif "artworks" in string:
				print("不支持下载插画，请重新输入")
				print("")
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


if __name__ == '__main__':
	path = "D:\\Users\\Administrator\\Desktop"
	main()
