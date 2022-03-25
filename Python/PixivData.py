#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from pixivpy3 import AppPixivAPI


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


def getNovelInfo(novel_id):
	json_result = aapi.novel_detail(novel_id)
	novel = json_result.novel
	title = novel.title

	date = novel.create_date[0:10]
	time = novel.create_date[11:19]
	datetime = date+ " "+ time
	
	total_bookmarks = novel.total_bookmarks
	total_view = novel.total_view
	total_comments = novel.total_comments
	return title, datetime, total_view, total_bookmarks, total_comments


def getIllustInfo(illust_id):
	json_result = aapi.illust_detail(illust_id)
	illust = json_result.illust
	title = illust.title
	
	date = illust.create_date[0:10]
	time = illust.create_date[11:19]
	datetime = date + " " + time
	
	total_bookmarks = illust.total_bookmarks
	total_view = illust.total_view
	total_comments = illust.total_comments
	return title, datetime, total_view, total_bookmarks, total_comments
	


def getUserInfo(user_id):
	string = ""
	json_result = aapi.user_detail(user_id)
	print(json_result)
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



def formatData(user_id):
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
		num = len(novelslist) - i
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


def SaveAsCsv(user_id, path):
	path = os.path.join(path, "数据.csv")
	text = formatData(user_id)
	if not os.path.exists(path):
		saveCsv(path, text)
	return path


def main():
	print("请输入Pixiv作者链接")
	print("")
	string = input()
	if re.search("[0-9]+", string):
		id = re.search("[0-9]+", string).group()
		if "pixiv.net" in string and "users" in string:
			print("开始下载此作者的阅读收藏评论数据")
			getUserInfo(id)
			SaveAsCsv(id, path)
            
	
if __name__ == '__main__':
	path = os.getcwd()
    main()
    