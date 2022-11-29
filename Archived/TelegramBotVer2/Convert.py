#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

from opencc import OpenCC

from FileOperate import openText, saveText
from PrintTags import printInfo


cc1 = OpenCC('tw2sp.json')  # 繁转简
cc2 = OpenCC('s2twp.json')  # 簡轉繁


def setPath(path):
	(path, name) = os.path.split(path)
	path1 = os.path.join(path, "简体", cc1.convert(name))  # 简体目录
	path2 = os.path.join(path, "繁體", cc2.convert(name))  # 繁体目录
	return path1, path2, name
	

def convert(path, language):
	# language Telegram 语言包
	text = openText(path)
	info = printInfo(path)
	(path1, path2, name) = setPath(path)
	
	if "zh_tw" in info and language == "zh-hans":
		text1 = cc1.convert(text)  # 繁体文件，转简体
		text1 = text1.replace("「", "“")
		text1 = text1.replace("」", "”")
		text1 = text1.replace("『", "‘")
		text1 = text1.replace("』", "’")
		saveText(path1, text1)     # 转简体，存简体目录
		info = cc1.convert(info)
		info = info.replace("#zh_tw", "#zh_cn #OpenCC")
		return path1, info
	
	elif "zh_cn" in info and language == "zh-hant":
		text2 = cc2.convert(text)  # 简体文件，转繁体
		text2 = text2.replace("“", "「")
		text2 = text2.replace("”", "」")
		text2 = text2.replace("‘", "『")
		text2 = text2.replace("’", "』")
		saveText(path2, text2)      # 转繁体，存繁体目录
		info = cc2.convert(info)
		info = info.replace("#zh_cn", "#zh_tw #OpenCC")
		return path2, info
	
	else:
		return None, None


if __name__ == "__main__":
	path = os.getcwd()
	path = os.path.join(path, "Novels")
