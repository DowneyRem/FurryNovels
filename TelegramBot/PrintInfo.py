#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
from platform import platform
from functools import cmp_to_key

from opencc import OpenCC

from MakeTags import hashtags, cntags, entags, racedict, racelist, cmp
from FileOperate import openText, openDocx, openDoc, findFile, timer
from Translate import getLanguage, transWords
from config import default_path, testMode


def sortTags(tags: set) -> str:  # 按dict内顺序对转换后的标签排序
	text = ""
	tags.discard("zh")
	li = list(tags)
	# li.reverse()  # 测试 sort 是否真正排序
	li.sort(key=cmp_to_key(cmp))
	for item in li:
		text += f"#{item} "
	# print(text)
	return text.strip()


def translateTags(tags: set) -> tuple[set, set]:  # 翻译标签
	tags1, tags2 = set(), set()  # tags1 翻译过的标签，tags2 无翻译的标签
	for tag in tags:
		tag = tag.replace("#", "")       # 去除#号
		tag1 = hashtags.get(tag, None)  # 获取英文标签, list 格式
		if tag1:
			for item in tag1:
				tags1.add(item)   # 用set去重
		else:
			tags2.add(tag)
	# print(tags1, tags2)
	return tags1, tags2


def getNormalTags(text: str, lang="") -> tuple[set, set]:  # 获取可能存在的标签
	characters = len(text)
	tags1, tags2 = set(), set()
	if "zh" in lang or "ja" in lang:
		textdict = cntags
	else:
		textdict = entags
		
	list1 = list(textdict.keys())
	list2 = list(textdict.values())
	for i in range(0, len(list1)):
		tag1 = list1[i]
		if text.count(tag1) > 5:  # 未测试
			# if 10000 * text.count(tag1) / characters > 15:
			# todo 引入总字数作基数？，如何添加剧情向小说的色情标签？ 如何添加剧情向标签？
			tags1.add(tag1)        # 汉字标签
			for tag2 in list2[i]:  # 英文标签，新数据格式list
				tags2.add(tag2)
	# print(tags1, tags2)
	return tags2, tags1  # 英文标签在前


def getRaceTags(text: str) -> tuple[set, set]:  # 获取可能存在的标签
	characters = len(text)
	tags1, tags2 = set(), set()
	list1 = list(racedict.keys())
	list2 = list(racedict.values())
	for i in range(0, len(list1)):
		tag1 = list1[i]
		if 10000 * text.count(tag1) / characters > 15:  # 已测试
			tags1.add(tag1)        # 汉字标签
			for tag2 in list2[i]:  # 英文标签，新数据格式list
				tags2.add(tag2)
	# print(tags1, tags2)
	return tags2, tags1  # 英文标签在前


@timer
def getFurryScore(text: str, tags: set) -> int:  # 计算兽人含量
	furry = 0
	tags1, tags2 = getRaceTags(text)
	tags3, tags4 = translateTags(tags)
	tags1.update(tags3)
	tags2.update(tags4)
	name = text[:100].split("\n")[0]
	racelist2 = list(racedict.keys())
	
	for race in tags1:  # 英文标签
		if race in racelist:
			furry += 1
	for race in tags2:  # 中文标签
		if race in racelist2:
			furry += 1
	
	words = "furry kemono 兽人 獸人 獣人 けもの ケモノ ケモホモ ホモケモ".split(" ")
	for word in words:
		if word in tags1 or word.capitalize() in tags1 or word.lower() in tags1 or word in tags2:
			furry += 2
			
	if __name__ == "__main__":  # 输出信息
		print(f"{name}福瑞指数：{furry:.1f}")
	return furry


def getTagsFromText(text: str, lang="") -> tuple[set, set]:  # 获取可能存在的标签
	tags1, tags2 = getNormalTags(text, lang)
	tags3, tags4 = getRaceTags(text)
	tags1.update(tags3)
	tags2.update(tags4)
	# print(tags1, tags2)
	return tags1, tags2  # 英文标签在前


def getFormattedTags(tags: set, text="", lang="") -> str:
	tags3 = ""
	tags0, tags2 = translateTags(tags)
	tags1 = sortTags(tags0)
	if tags2:
		tags2 = f"特殊：{sortTags(tags2)}\n"
	
	if text:
		unsure1, unsure2 = getTagsFromText(text, lang)  # 英文在前
		if unsure1:
			unsure1 = unsure1.difference(tags0)  # 去重，获取作者未标注的标签
			unsure1 = sortTags(unsure1)
			unsure2 = sortTags(unsure2)
			if "Linux" in platform():
				tags3 = f"可能存在：{unsure1}"
			else:
				tags3 = f"可能存在：{unsure1}\n{unsure2}"
	
	info = f"{tags1}\n{tags2}{tags3}".strip()
	# if __name__ == "__main__":  # 输出信息
	# 	print(f"tags: {info}\n")
	return info
	
	
# 根据文本，输出文件信息
def getInfoFromText(text: str, tags="", lang="", *, num=0) -> str:
	if not lang:
		lang = getLanguage(text)
		
	textlist = text[:500].split("\n")[:4]
	if "zh_cn" in lang and __name__ != "__main__":   # 调用时转换
		title = OpenCC('s2twp.json').convert(textlist[0])
	elif "zh_tw" in lang and __name__ != "__main__":
		title = OpenCC('tw2sp.json').convert(textlist[0])
	else:
		title = textlist[0]
		
	if num:
		title = f"第{num}篇：{title}"
	author = f'by #{textlist[1].replace(transWords("author", lang), "")}'
	url = textlist[2].replace(transWords("url", lang), "")
	if not tags:
		tags = textlist[3].replace("标签：", "").replace("標籤：", "")
		tags = set(tags.replace(transWords("hashtags", lang), "").split(" #"))
		tags.add(lang)
		
	tags = getFormattedTags(tags, text, lang)
	info = f"{title}\n{author}\n{tags}\n{url}".strip()
	if __name__ == "__main__":  # 输出信息
		print(f"{info}\n")
	return info


def printTags(path: str, *, num=0):
	text = ""
	name = os.path.split(path)[1]
	ext = os.path.splitext(path)[1]
	
	if ext == ".txt":
		text = openText(path)
	elif ext == ".docx":
		try:
			text = openDocx(path)
		except Exception as e:
			logging.warning(e)
			try:
				text = openDoc(path)
			except Exception as e:
				logging.warning(e)
	elif ext == ".doc" and "Windows" in platform():
		text = openDoc(path)
	else:
		print(f"当前文件：{name}暂不支持打印相关信息")
	if text:
		getInfoFromText(text, num=num)
	

@timer
def main(path=default_path):
	files = findFile(path, ".docx", ".txt")
	# files = findFile(path, ".docx", ".txt", ".doc")
	for i in range(len(files)):
		file = files[i]
		printTags(file, num=i+1)
	
	
@timer
def test():
	print("测试")
	path = r"D:\Download\Github\FurryNovelsBot\Novels\2022\09\雷狼龙之殇.txt"
	# path = r"D:\Download\Github\FurryNovelsBot\Novels\2022\08\当社畜不如变胶龙.txt"
	printTags(path)
	

if __name__ == "__main__":
	testMode = 0
	if testMode:
		test()
	else:
		main()
		
