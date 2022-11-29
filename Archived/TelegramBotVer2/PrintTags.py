#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
from platform import platform
from functools import cmp_to_key

from opencc import OpenCC

from ver2.DictNovel import noveldict, cmp  # 小说标签
from ver2.DictText import textdict  # 正文关键词
from ver2.DictRace import racedict  # 种族关键词
from FileOperate import findFile, openText, openText4, openDocx, openDocx4, unzipFile
from PixivNovels import getSeriesId, formatSeriesInfo

if "小说推荐" in os.getcwd():
	from FileOperate import monthNow, openNowDir


cc1 = OpenCC('tw2sp.json')  # 繁转简
cc2 = OpenCC('s2twp.json')  # 簡轉繁


def sortTags(set, cmp):  # 按dict内顺序对转换后的标签排序
	text = ""
	li = list(set)
	li.sort(key=cmp_to_key(cmp))
	
	for i in range(len(li)):
		taglist = li[i].split()  # 一关键词匹配多标签
		for j in range(len(taglist)):
			tag = taglist[j]
			# print(tag)
			text += "#{} ".format(tag)
	return text


def translateTags(tags):  # 获取英文标签
	taglist = tags.split()
	tags2 = ""; s = set()
	for i in range(0, len(taglist)):
		tag = taglist[i]
		tag = tag.replace("#", "")
		tag = noveldict.get(tag)  # 获取英文标签
		
		if tag is not None:
			for i in tag:  # 处理修改后的数据格式 list
				s.add(i)   # 获取到的标签利用set去重
		else:
			tag = taglist[i]
			tags2 += tag + " "
	return s, tags2


def getTags(text):  # 获取可能存在的标签
	# 引入总字数作基数的话，如何避免无法获得剧情向小说色情标签？
	# 优势，色情标签过少可以添加 #剧情向标签
	s1 = set(); s2 = set()
	list1 = list(textdict.keys())
	list2 = list(textdict.values())
	for i in range(0, len(list1)):
		a = list1[i]
		num = text.count(a)
		if num > 5:  # 数据未测试
			s1.add(list1[i])   # 汉字标签
			for j in list2[i]: # 英文标签，新数据格式list
				s2.add(j)
	return s2, s1  # 英文标签在前


def getRaceTags(text):  # 获取可能存在的种族职业标签
	s1 = set(); s2 = set()
	textnum = len(text)
	list1 = list(racedict.keys())
	list2 = list(racedict.values())
	for i in range(0, len(list1)):
		a = list1[i]
		num = text.count(a)
		if 10000 * num / textnum > 15:  # 神奇的数据
			s1.add(list1[i])   # 汉字标签
			for j in list2[i]: # 英文标签，新数据格式list
				s2.add(j)
	return s2, s1  # 英文标签在前

			
def getInfo(text, textlist):
	name = textlist[0]
	authro = textlist[1].replace("作者：", "")
	authro = authro.replace("Author: ", "")
	authro = "by #" + authro
	
	url = textlist[2].replace("网址：", "")
	url = url.replace("網址：", "")
	url = url.replace("链接：", "")
	url = url.replace("URL: ", "")
	
	tags = textlist[3].replace("标签：", "")
	tags = tags.replace("標簽：", "")
	tags = tags.replace("標籤：", "")
	tags = tags.replace("Tags: ", "")
	tags = tags.replace("#", " #")
	tags = cc1.convert(tags)  # 转简体，只处理简体标签
	(tags1, tags2) = translateTags(tags)  # 获取已翻译/未翻译的标签
	# print(tags2)
	
	if "#zh_cn" in tags:
		name = cc2.convert(textlist[0])
	elif "#zh_tw" in tags:
		name = cc1.convert(textlist[0])
	
	text = cc1.convert(text)  # 按照简体文本处理关键词获取对应标签
	(unsure1, unsure2) = getRaceTags(text)
	(unsure3, unsure4) = getTags(text)
	s1 = unsure1.union(unsure3)
	s2 = unsure2.union(unsure4)
	
	unsuretag = ""
	if s1 != set():
		s1 = s1.difference(tags1)  # 去重，获取作者未标注的标签
		s1 = sortTags(s1, cmp)
		s2 = sortTags(s2, cmp)
		
		if "小说推荐" in os.getcwd():
			unsuretag = "可能存在：" + s1 + "\n" + s2 + "\n"
		else:
			unsuretag = "可能存在：" + s1 + "\n" # + s2
	
	tags1 = sortTags(tags1, cmp)
	if tags2 != "":
		tags2 = "特殊：{}\n".format(tags2)
	info = f"{name}{authro}{tags1}\n{tags2}{unsuretag}{url}"
	# info = "{}{}{}\n{}{}{}".format(name, authro, tags1, tags2, unsuretag, url)
	
	if "Windows" in platform():
		print(info)
	return info


def printInfo(path):
	(dir, name) = os.path.split(path)
	(name, ext) = os.path.splitext(name)
	if ext == ".docx":
		textlist = openDocx4(path)
		text = openDocx(path)
	elif ext == ".txt":
		textlist = openText4(path)
		text = openText(path)
		
	elif ext == ".zip":
		text = ""  # 处理zip合集
		path = unzipFile(path)
		filelist = findFile(path, ".txt")
		for i in range(len(filelist)):
			file = filelist[i]
			text += openText(file)

		urltext = openText4(filelist[1])[2]
		novelid = re.findall("[0-9]{5,}", urltext)[0]
		seriesid = getSeriesId(novelid)[0]
		
		caption = formatSeriesInfo(seriesid)
		caption = re.sub("其他：.*\n?", "", caption, 1)
		caption = caption.replace("\n", "\n\t")
		textlist = caption.split("\t")
		
	else:
		print("文件类别不在可以处理的范围内")
	
	if len(textlist) >= 4:
		info = getInfo(text, textlist)
	else:
		info = "【{}】未处理".format(name)
	return info


def getPath(path):
	j = 0
	dirstr = monthNow()  # 只处理本月的文件
	pathlist = findFile(path, ".docx", ".txt")
	for i in range(0, len(pathlist)):
		filepath = pathlist[i]
		printInfo(filepath)
		if dirstr in filepath:
			j += 1
			
	if "小说推荐" in os.getcwd():
		if j != 0:
			openNowDir()
		else:
			print("本月 " + dirstr + " 无新文档")


if __name__ == "__main__":
	# path = os.getcwd()
	# if "小说推荐" in path:
	# 	path = path.replace("\工具", "")
	# else:
	# 	path = os.path.join(path, "Novels")
	#
	# print("本月文档如下：\n")
	# getPath(path)
	pass
	print(list(racedict.values()))
