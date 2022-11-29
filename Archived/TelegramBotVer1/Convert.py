#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from FileOperate import openText, saveText
from PrintTags import printInfo
from config import cc1, cc2


def getPath(path):
	(path, name) = os.path.split(path)
	path1 = os.path.join(path, "简体版" , cc1.convert(name))  # 简体目录
	path2 = os.path.join(path, "繁體版" , cc2.convert(name))  # 繁体目录
	return path1, path2, name


def translate(path, language):
	text = openText(path)
	info = printInfo(path)
	(path1, path2, name) = getPath(path)
	
	if "zh_tw" in info and language == "zh-hans":
		text1 = cc1.convert(text)  # 繁体文件，转简体
		saveText(path1, text1)     # 转简体，存简体目录
		info = cc1.convert(info)
		return path1 #, info
	
	elif "zh_cn" in info and language == "zh-hant":
		text2 = cc2.convert(text)  # 简体文件，转繁体
		saveText(path2, text2)     # 转繁体，存繁体目录
		info = cc2.convert(info)
		return path2 #, info
	else:
		return path #, info



if __name__ == "__main__":
	path = os.getcwd()
	path = os.path.join(path, "Novels")
	