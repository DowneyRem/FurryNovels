#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import shutil
import time
from functools import wraps


pathlist = []


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
			except IOError:
				print("文件被占用：{}".format(arg))
		else:
			print("文件不存在：{}".format(arg))
	return wrapper


def saveFileCheck(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		arg = args[0]
		(dir, name) = os.path.split(arg)  # 分离文件名和目录名
		if not os.path.exists(dir):
			os.makedirs(dir)
		r = func(*args, **kwargs)
		return r
	return wrapper


def findFile(path, *extnames):
	# 省略 extnames 参数可以获取全部文件
	for dir in os.listdir(path):
		dir = os.path.join(path, dir)
		if os.path.isdir(dir):
			findFile(dir, *extnames)
		
		if os.path.isfile(dir):
			if len(extnames) > 0:
				for extname in extnames:
					(name, ext) = os.path.splitext(dir)
					if ext == extname:
						pathlist.append(dir)
			elif len(extnames) == 0:
				pathlist.append(dir)
	return pathlist


@openFileCheck
def openText(path):
	text = ""
	try:
		with open(path, "r", encoding="UTF8") as f:
			text = f.read()
	except UnicodeError:
		try:
			with open(path, "r", encoding="GBK") as f:
				text = f.read()
		except UnicodeError:  # Big5 似乎有奇怪的bug，不过目前似乎遇不到
			with open(path, "r", encoding="BIG5") as f:
				text = f.read()
	finally:
		return text


@saveFileCheck
def saveText(path, text):
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	try:
		with open(path, "w", encoding="UTF8") as f:
			f.write(text)
		print("已保存：【{}】".format(name))
	except IOError:
		print("保存失败：【{}】".format(name))


def formatPixivText(text):
	# 处理Pixiv 标识符，转换成普通文本
	
	# [newpage]  [chapter: 本章标题]
	text = text.replace("[newpage]", "\n\n")
	a = re.findall("\[chapter:(.*)]", text)
	for i in range(len(a)):
		string = a[i]
		if "第" in string and "章" in string:
			pass
		elif re.search("[0-9]+", string):
			string = "第{}章".format(string)
		elif re.search("[二三四五六七八九]?[十]?[一二三四五六七八九十]", string):
			string = "第{}章".format(string)
		text = re.sub("\[chapter:(.*)\]", string, text, 1)
	
	
	# [jump: 链接目标的页面编号]
	a = re.findall("\[jump:(.*)\]", text)
	for i in range(len(a)):
		string = a[i]
		string = "跳转至第{}节".format(string)
		text = re.sub("\[jump:(.*)\]", string, text, 1)
	
	
	# [pixivimage: 作品ID]
	a = re.findall("\[pixivimage: (.*)\]", text)
	for i in range(len(a)):
		string = a[i].strip(" ")
		string = "插图：https://www.pixiv.net/artworks/{}".format(string)
		text = re.sub("\[pixivimage:(.*)\]", string, text, 1)
	
	
	# [uploadedimage: 上传图片自动生成的ID]
	# 会被 pixivpy 自动转换成一下这一大串
	pattern = "\[\[jumpuri:If you would like to view illustrations, please use your desktop browser.>https://www.pixiv.net/n/[0-9]{5,}\]\]"
	string = "【本文内有插图，请在Pixv查看】"
	text = re.sub(pattern, string, text)


	# [[jumpuri: 标题 > 链接目标的URL]]
	pattern = "\[{2}jumpuri: *(.*)>(.*)\]{2}"
	a = re.findall(pattern, text)
	for i in range(len(a)):
		name = a[i][0].strip(" ")
		link = a[i][1].strip(" ")
		if link in name:
			text = re.sub(pattern, link, text, 1)
		elif "点我看图" in name:
			text = re.sub(pattern, "", text, 1)
		else:
			string = "{}：\n{}".format(name, link)
			text = re.sub(pattern, string, text, 1)
	
	text = re.sub("\n{3,}", "\n\n\n", text)
	# print(text)
	return text


def formatNormalText(text):
	# 普通文本转换成 Pixiv 标识符
	
	# [newpage]  [chapter: 本章标题]
	pattern = "(第.*章) (.*)\\n"
	a = re.findall(pattern, text)
	for i in range(len(a)):
		num  = a[i][0]
		name = a[i][1]
		pattern = "{} ?{}".format(num, name)
		# if "1" in num or "一" in num:
		# 	string = "[chapter:{} {}]".format(num, name)
		string = "[newpage]\n[chapter:{} {}]".format(num, name)
		text = re.sub(pattern, string, text, 1)
		
	pattern = "(完结感言|关于本文|作者的话) ?.*\\n"
	a = re.findall(pattern, text)
	for i in range(len(a)):
		name = a[i]
		pattern = "{} ?".format(name)
		string = "[chapter:{}]".format(name)
		text = re.sub(pattern, string, text, 1)
	
	
	# [pixivimage: 作品ID]
	pattern = "((?:https?://)?www\.pixiv\.net/artworks/([0-9]{5,}))"
	a = re.findall(pattern, text)
	for i in range(len(a)):
		link  = a[i][0]
		artid = a[i][1]
		str1 = "[pixivimage: {}]".format(artid)
		str2 = "[[jumpuri: 点我看图 > https://www.pixiv.net/artworks/{} ]]".format(artid)
		string = "{}\n{}".format(str1, str2)
		text = re.sub(link, string, text, 1)
		
	
	# [[jumpuri: 标题 > 链接目标的URL]]
	pat = "(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"
	s1 = set(re.findall(pat, text))
	pattern = "(.*)(?:：|？)\n?({})".format(pat)  # 有名称的链接
	b = re.findall(pattern, text)
	pattern = "\[\[jumpuri:.* ?> ?({})".format(pat)  # 排除已经处理过的链接
	s3 = set(re.findall(pattern, text))
	
	s2 = set()
	for t in b:  # 处理有名称的链接
		name = t[0]
		link = t[1]
		string = "[[jumpuri: {0} > {1} ]]".format(name, link)
		pattern = "{}：?\n?".format(name)
		text = text.replace(link, "")
		text = re.sub(pattern, string, text, 1)
		s2.add(link)
	
	s1 = s1.difference(s2, s3)
	for link in s1:  # 处理无名称的链接
		string = "[[jumpuri: {0} > {0} ]]".format(link)
		text = re.sub(link, string, text, 1)
	
	text = re.sub("\n{3,}", "\n\n\n", text)
	# print(text)
	return text


def convert(path):
	list = findFile(path, ".txt")
	for path in list:
		(dir, name) = os.path.split(path)
		text = openText(path)
		if "[chapter:" in text:
			name = name.replace(".txt", "-净化版.txt")
			text = formatPixivText(text)
		else:
			name = name.replace(".txt", "-Pixiv版.txt")
			text = formatNormalText(text)
			
		path = os.path.join(dir, "转换版", name)
		saveText(path, text)


def main():
	path = os.getcwd()
	dir = os.path.join(path, "转换版")
	if os.path.exists(dir):
		try:
			shutil.rmtree(dir)
		except:
			print("文件被占用")
			# os.system("chcp 65001")
			# os.system("Pause")
	print("智能转换中……")
	convert(path)
	
	
if __name__ == '__main__':
	main()
