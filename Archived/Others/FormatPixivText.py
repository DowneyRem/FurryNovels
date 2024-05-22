#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import shutil
import re
import time
from functools import wraps


pathlist = []


def timer(func):
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
				print(f"文件被占用：{arg}")
		else:
			print(f"文件不存在：{arg}")
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
					if ext == extname and "转换版" not in dir:
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
	dir, name = os.path.split(path)
	try:
		with open(path, "w", encoding="UTF8") as f:
			f.write(text)
		print(f"已转换为：【{name}】")
	except IOError:
		print(f"保存失败：【{name}】")


def format2NormalText(text):
	# 处理Pixiv 标识符，转换成普通文本
	
	if "[chapter:" in text:
		a = re.findall("\[chapter:(.*)]", text)
		for i in range(len(a)):
			string = a[i]
			if "第" in string and "章" in string:
				pass
			elif re.search("[0-9]+", string):
				string = f"第{string}章"
			elif re.search("[二三四五六七八九]?[十]?[一二三四五六七八九十]", string):
				string = f"第{string}章"
			text = re.sub("\[chapter:(.*)]", string, text, 1)
	
	# [jump: 链接目标的页面编号]
	if "[jump:" in text:
		a = re.findall("\[jump:(.*)]", text)
		for i in range(len(a)):
			string = a[i]
			string = f"跳转至第{string}节"
			text = re.sub("\[jump:(.*)]", string, text, 1)
	
	# [pixivimage: 作品ID]
	if "[pixivimage:" in text:
		a = re.findall("\[pixivimage: (.*)]", text)
		for i in range(len(a)):
			string = a[i].strip(" ")
			string = f"插图：https://www.pixiv.net/artworks/{string}"
			text = re.sub("\[pixivimage:(.*)]", string, text, 1)
	
	# [uploadedimage: 上传图片自动生成的ID] 会被 pixivpy 自动转换成以下一大串
	if "[jumpuri:If" in text:
		pattern = "\[{2}jumpuri:If you would like to view illustrations, please use your desktop browser.>https://www.pixiv.net/n/[0-9]{5,}\]{2}"
		string = "【本文内有插图，请在Pixv查看】"
		text = re.sub(pattern, string, text)
	
	# [[jumpuri: 标题 > 链接目标的URL]]
	if "[[jumpuri:" in text:
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
				string = f"{name}：\n{link}"
				text = re.sub(pattern, string, text, 1)
	
	# [newpage]  [chapter: 本章标题]
	if "[newpage]" in text:
		text = text.replace("[newpage]", "\n\n")
	# text = re.sub("\n{3,}", "\n\n\n", text)
	
	# print(text)
	return text


def format2PixivText(text):
	# 普通文本转换成 Pixiv 标识符
	
	# [newpage]  [chapter: 本章标题]
	pattern = "(第.*章) (.*)\\n"
	if re.findall(pattern, text):
		a = re.findall(pattern, text)
		for i in range(len(a)):
			num  = a[i][0]
			name = a[i][1]
			pattern = f"{num} ?{name}"
			# if "1" in num or "一" in num:
			# 	string = f"[chapter:{} {}]"
			string = f"[newpage]\n[chapter:{num} {name}]"
			text = re.sub(pattern, string, text, 1)
		
	pattern = "(完结感言|关于本文|作者的话) ?.*\\n"
	if re.findall(pattern, text):
		a = re.findall(pattern, text)
		for i in range(len(a)):
			name = a[i]
			pattern = "{} ?".format(name)
			string = "[chapter:{}]".format(name)
			text = re.sub(pattern, string, text, 1)
	
	# [pixivimage: 作品ID]
	pattern = "((?:https?://)?www\.pixiv\.net/artworks/([0-9]{5,}))"
	if re.findall(pattern, text):
		a = re.findall(pattern, text)
		for i in range(len(a)):
			link  = a[i][0]
			artid = a[i][1]
			str1 = "f[pixivimage: {artid}]"
			str2 = "f[[jumpuri: 点我看图 > https://www.pixiv.net/artworks/{artid} ]]"
			string = "{str1}\n{str2}"
			text = re.sub(link, string, text, 1)
			
	# [[jumpuri: 标题 > 链接目标的URL]]
	pat = "(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"  # url
	if re.findall(pat, text):
		s1 = set(re.findall(pat, text))
		pattern = f"(.*)(?:：|？)\n?({pat})"      # 有名称的链接
		b = re.findall(pattern, text)
		pattern = f"\[\[jumpuri:.* ?> ?({pat})"  # 排除已经处理过的链接
		s3 = set(re.findall(pattern, text))
		
		s2 = set()
		for t in b:  # 处理有名称的链接
			name = t[0]
			link = t[1]
			string = f"[[jumpuri: {name} > {link} ]]"
			pattern = f"{name}：?\n?"
			text = text.replace(link, "")
			text = re.sub(pattern, string, text, 1)
			s2.add(link)
		
		s1 = s1.difference(s2, s3)
		for link in s1:  # 处理无名称的链接
			string = f"[[jumpuri: {link} > {link} ]]"
			text = re.sub(link, string, text, 1)
	
	# text = re.sub("\n{3,}", "\n\n\n", text)
	# print(text)
	return text


def convert(path):
	dir, name = os.path.split(path)
	text = openText(path)
	if "[chapter:" in text:
		name = name.replace(".txt", "-净化版.txt")
		text = format2NormalText(text)
	else:
		name = name.replace(".txt", "-Pixiv版.txt")
		text = format2PixivText(text)
		
	path = os.path.join(dir, "转换版", name)
	saveText(path, text)
	return path


def main():
	path = os.getcwd()
	dir = os.path.join(path, "转换版")
	if os.path.exists(dir):
		try:
			shutil.rmtree(dir)
			print("已删除上次转换文件")
		except IOError:
			print("文件被占用，无法删除上次转换文件")
			time.sleep(3)
		
	pathlist = findFile(path, ".txt")
	if len(pathlist) == 0:
		print("当前文件夹下无txt文件\n请把txt文件放在当前文件夹下")
	else:
		print("智能转换中……")
		for path in pathlist:
			convert(path)
		print("转换完成")
	time.sleep(5)
	
	
if __name__ == '__main__':
	main()
