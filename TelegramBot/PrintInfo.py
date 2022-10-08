#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
from platform import platform
from functools import cmp_to_key

from opencc import OpenCC

from MakeTags import hashtags, cntags, entags, racetags, racedict, racelist, cmp
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
	hashtags.update(racetags)
	tags1, tags2 = set(), set()  # tags1 翻译过的标签，tags2 无翻译的标签
	for tag in tags:
		tag = tag.replace("#", "").lower()  # 去除#号
		tag1 = hashtags.get(tag, None)  # 获取英文标签, list 格式
		if tag1:
			for item in tag1:
				tags1.add(item)   # 用set去重
		else:
			tags2.add(tag)
	# print(tags1, tags2)
	return tags1, tags2


def getTagsFromText(text: str, lang="") -> tuple[set, set]:  # 获取可能存在的标签
	dict0 = racedict.copy()
	if not lang:  # 默认使用 racedict
		times = 5  # 15过高；
	else:
		times = 5
		if "zh" in lang or "ja" in lang:
			dict0.update(cntags)
		else:
			dict0.update(entags)
			
	tags1, tags2 = set(), set()
	for tag1 in dict0:
		if 10000 * text.count(tag1) / len(text) >= times:
			tags1.add(tag1)  # 汉字标签
			for tag2 in dict0[tag1]:  # 英文标签，新数据格式list
				tags2.add(tag2)
		
	# if tags1 != set():
	# 	logging.info(f"{tags1}, {tags2}")
	return tags2, tags1  # 英文标签在前
	
	
def getFurryScore(tags1: set, tags2: set, tags3: set, tags4: set) -> int:  # 计算兽人含量
	furry = 0
	entags = tags1.union(tags3)
	cntags = tags2.union(tags4)
	# racelist2 = list(racedict.keys())
	# print(entags, cntags, sep="\n")
	
	for race in entags:
		if race.lower() in racelist:
			furry += 2
	for race in cntags:
		if race in racedict.keys():
			furry += 2
	return furry


def getFormattedTags(tags: set) -> str:  # 简化的 formatTags，用于系列zip合集
	tags1, tags2 = translateTags(tags)
	if tags2:
		tags2 = f"特殊：{sortTags(tags2)}\n"
	else:
		tags2 = ""
	info = f"{sortTags(tags1)}\n{tags2}".strip()
	return info


def formatTags(tags1: set, tags2: set, unsure1: set, unsure2: set) -> str:
	tags3 = ""
	if unsure1:
		unsure1 = unsure1.difference(tags1)  # 去重，获取作者未标注的标签
		if "Linux" in platform():
			tags3 = f"可能存在：{sortTags(unsure1)}"
		else:
			tags3 = f"可能存在：{sortTags(unsure1)}\n{sortTags(unsure2)}"
	
	if tags2:
		tags2 = f"特殊：{sortTags(tags2)}\n"
	else:
		tags2 = ""
	tags = f"{sortTags(tags1)}\n{tags2}{tags3}".strip()
	# if __name__ == "__main__":  # 输出信息
	# 	print(f"tags: {info}\n")
	return tags
	
	
# 根据文本，输出文件信息
def getInfoFromText(text: str, tags="", lang="", *, num=0) -> tuple[str, int]:
	if not lang:
		lang = getLanguage(text)
		
	textlist = text[:500].split("\n")[:4]
	author = f'by #{textlist[1].replace(transWords("author", lang), "")}'
	url = textlist[2].replace(transWords("url", lang), "")
	
	if "zh_cn" in lang and __name__ != "__main__":   # 调用时转换
		title = OpenCC('s2twp.json').convert(textlist[0])
	elif "zh_tw" in lang and __name__ != "__main__":
		title = OpenCC('tw2sp.json').convert(textlist[0])
	else:
		title = textlist[0]
		
	if num:
		title = f"第{num}篇：{title}"
	if not tags:
		tags = textlist[3].replace("标签：", "").replace("標籤：", "")
		tags = set(tags.replace(transWords("hashtags", lang), "").split(" #"))
		tags.add(lang)
	
	tags1, tags2 = translateTags(tags)
	tags3, tags4 = getTagsFromText(text, lang)
	tags = formatTags(tags1, tags2, tags3, tags4)
	furry = getFurryScore(tags1, tags2, tags3, tags4)
	info = f"{title}\n{author}\n{tags}\n{url}".strip()
	if __name__ == "__main__":  # 输出信息
		print(f"{info}\n福瑞指数：{furry:.1f}\n")
	return info, furry


def printInfo(path: str, *, num=0):
	text = ""
	name = os.path.split(path)[1]
	ext = os.path.splitext(path)[1]
	
	if ext.lower() == ".txt":
		text = openText(path)
	elif ext.lower() == ".docx":
		try:
			text = openDocx(path)
		except Exception as e:
			logging.warning(e)
			try:
				text = openDoc(path)
			except Exception as e:
				logging.warning(e)
	elif ext.lower() == ".doc" and "Windows" in platform():
		try:
			text = openDoc(path)
		except Exception as e:
			logging.warning(e)
	else:
		print(f"当前文件：{name}暂不支持打印相关信息")
	if text:
		getInfoFromText(text, num=num)
	

@timer
def main(path=default_path):
	if "Windows" in platform():
		files = findFile(path, ".txt", ".docx", ".doc")
	else:
		files = findFile(path, ".txt", ".docx")
		
	for i in range(len(files)):
		file = files[i]
		printInfo(file, num=i+1)
	
	
@timer
def test():
	print("测试")

	

if __name__ == "__main__":
	# testMode = 1
	if testMode:
		test()
	else:
		main()
		
