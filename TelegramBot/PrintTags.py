#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from functools import cmp_to_key
from DictNovel import noveldict, cmp   #小说标签
from DictText import textdict          #正文关键词
from DictRace import racedict          #种族关键词
from FileOperate import findFile, openText, openText4, openDocx, openDocx4
from config import cc1, cc2


def set2Text(set):
	text = str(set)
	text = text.replace("{", "")
	text = text.replace("}", "")
	text = text.replace("'", "")
	text = text.replace(",", "")
	return text


def sortTags(set, cmp):  # 按dict内顺序对转换后的标签排序
	text = ""
	li = list(set)
	li.sort(key=cmp_to_key(cmp))
	
	for i in range(len(li)):
		taglist = li[i].split()    # 一关键词匹配多标签
		for j in range(len(taglist)):
			tag = taglist[j]
			# print(tag)
			text += "#{} ".format(tag)
	return text


def addTags(text):  # 添加靠谱的标签
	list1 = "邊 變 並 從 點 東 對 發 該 個 給 關 過 還 後 歡 會 機 幾 間 見 將 進 經 覺 開 來 裡 兩 嗎 麼 沒 們 難 讓 時 實 說 雖 為 問 無 現 樣 應 於 與 則 這 種".split(" ")
	list3 = "边 变 并 从 点 东 对 发 该 个 给 关 过 还 后 欢 会 机 几 间 见 将 进 经 觉 开 来 里 两 吗 么 没 们 难 让 时 实 说 虽 为 问 无 现 样 应 于 与 则 这 种".split(" ")
	# 语料库来自 https://elearning.ling.sinica.edu.tw/cwordfreq.html
	# 从中选取前三百的繁体字部分，并在文章中随机检验，取存在率最高的前50个繁体字符
	
	tags = ""; j = 0; list2 = []
	for i in range(len(list1)):
		char = list1[i]
		num = text.count(char)
		if num >= 5:
			j += 1
			list2.append(char)
	
	tags += " #txt #finished "
	if j >= 0.2 * len(list1):
		tags += "#zh_tw"
	else:
		tags += "#zh_cn"
	return tags


def translateTags(taglist):  # 获取英文标签
	tags2 = ""; s = set()
	for i in range(0, len(taglist)):
		tag = taglist[i]
		tag = tag.replace("#", "")
		tag = tag.replace(" ", "")
		tag = tag.replace("　", "")
		tag = noveldict.get(tag)  # 获取英文标签
		
		if tag != None:
			s.add(tag)  # 获取到的标签利用set去重
		else:
			tag = taglist[i]
			tags2 += tag + " "
	return s, tags2


def getRaceTags(text):  # 获取可能存在的标签
	s1 = set(); s2 = set()
	textnum = len(text)
	list1 = list(racedict.keys())
	list2 = list(racedict.values())
	for i in range(0, len(list1)):
		a = list1[i]
		num = text.count(a)
		if 10000 * num / textnum > 15:  #神奇的数据
			s1.add(list1[i])  # 汉字标签
			s2.add(list2[i])  # 英文标签
	return s2, s1  # 英文标签在前


def getTags(text):  # 获取可能存在的标签
	s1 = set(); s2 = set()
	list1 = list(textdict.keys())
	list2 = list(textdict.values())
	for i in range(0, len(list1)):
		a = list1[i]
		num = text.count(a)
		if num > 5:        #数据未测试
			s1.add(list1[i])  # 汉字标签
			s2.add(list2[i])  # 英文标签
	return s2, s1  # 英文标签在前


def setSpilt(s1):
	s1 = set2Text(s1)
	s1 = s1.split(" ")  # 允许一关键词对多标签，并拆分成处理
	s1 = set(s1)
	return s1


def getInfo(text, textlist):
	authro = textlist[1].replace("作者：", "")
	authro = "by #" + authro
	
	url = textlist[2].replace("网址：", "")
	url = url.replace("網址：", "")
	url = url.replace("链接：", "")
	url = url + "\n"
	
	tags = textlist[3].replace("标签：", "")
	tags = tags.replace("標簽：", "")
	tags += addTags(text)  # 新增 #zh_tw 或 #zh_cn
	tags = cc1.convert(tags)  # 转简体，只处理简体标签
	list = tags.split()
	(tags1, tags2) = translateTags(list)  # 获取已翻译/未翻译的标签

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
		s1 = setSpilt(s1)
		tags1 = setSpilt(tags1)    #拆分一关键词对多个标签
		s1 = s1.difference(tags1)  #去重，获取作者未标注的标签
		s1 = sortTags(s1, cmp)
		s2 = sortTags(s2, cmp)
		unsuretag = "可能存在："+ s1 #+ s2
	
	tags1 = sortTags(tags1, cmp)
	if tags2 != "":
		tags2 = "特殊：{}\n".format(tags2)
	info = "{}{}{}\n{}{}\n{}".format(name, authro, tags1, tags2, unsuretag, url)
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
	
	if len(textlist) >= 4:
		info = getInfo(text, textlist)
		# print(info)  # 格式化输出
	else:
		info = "【{}】未处理".format(name)
		print(info)
		print("")
	return info


def getPath(path):
	pathlist = findFile(path, ".docx", ".txt")
	for i in range(0, len(pathlist)):
		filepath = pathlist[i]
		printInfo(filepath)


def main():
	print("本月文档如下：")
	print("\n" * 2)
	getPath(path)


if __name__ == "__main__":
	path = os.getcwd()
	path = os.path.join(path, "Novels")
	pass
