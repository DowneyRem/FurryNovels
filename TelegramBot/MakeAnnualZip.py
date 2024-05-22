#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

from opencc import OpenCC

from FileOperate import findFile, readFile, saveFile, zipFile, removeFile, timer
from GetLanguage import getLanguage
from Webdav4 import uploadFile, downloadFiles
from configuration import PASSWORD


def convert(text: str, lang1=""):
	if "zh_tw" in lang1:
		text2 = OpenCC('tw2sp.json').convert(text)  # 繁体文件，转简体
		text2 = text2.replace("「", "“").replace("」", "”").replace("『", "‘").replace("』", "’")
	else:
		text2 = OpenCC('s2twp.json').convert(text)  # 简体文件，转繁体
		text2 = text2.replace("“", "「").replace("”", "」").replace("‘", "『").replace("’", "』")
	return text2
	
	
def convertText(text: str, lang1=""):  # 原来是 language Telegram 语言包
	# lang1 原语言， lang2 目标语言
	if not lang1:
		lang1 = getLanguage(text)
	text2 = convert(text, lang1=lang1)
	
	if lang1 == "zh_cn":
		return text, text2
	else:
		return text2, text


def convertPath(filepath: str, lang1):
	path = os.getcwd()
	filepath = filepath.replace(".docx", ".txt")
	partpath = os.path.relpath(filepath, path)
	# print(path, partpath, sep="\n")
	path1 = os.path.join(path, "简体版", convertText(partpath, lang1=lang1)[0])
	path2 = os.path.join(path, "繁體版", convertText(partpath, lang1=lang1)[1])
	# print(path1, path2, sep="\n")
	return path1, path2
	

def convertFile(path):
	text = readFile(path)
	lang = getLanguage(text)
	text1, text2 = convertText(text, lang1=lang)
	path1, path2 = convertPath(path, lang1=lang)
	saveFile(path1, text1)
	saveFile(path2, text2)
	return path1, path2


def removeFiles():
	path = os.getcwd()
	path1 = os.path.join(path, "简体版")
	path2 = os.path.join(path, "繁體版")
	removeFile([path1, path2])
	
	
@timer
def convertFiles(files: list):
	for i in range(len(files)):
		file = files[i]
		if "简体版" not in file and "繁體版" not in file:
			name = os.path.basename(file).replace(os.path.splitext(file)[1], "")
			convertFile(file)
			rate = round(100 * i / len(files))
			print(f"【{name}】已转换，当前进度{rate}%")
	print("转换完成，开始压缩")
	
	
@timer
def makeZipFile(path0):
	path, folder = os.path.split(path0)
	# print(path, folder)
	# path0 = os.path.join(path, folder)
	path1 = os.path.join(path, "简体版", folder)
	path2 = os.path.join(path, "繁體版", folder)
	# print(path1, path2, sep="\n")
	
	zippath0 = os.path.join(path, f"{folder} 合集.zip")
	zippath1 = os.path.join(path, f"{folder} 合集 简体版.zip")
	zippath2 = os.path.join(path, f"{folder} 合集 繁體版.zip")
	zippath3 = os.path.join(path, f"{folder} 合集 简体版 密码：{PASSWORD}.zip")
	# print(zippath1, zippath2, sep="\n")
	
	zipFile(path0, zippath=zippath0, password="")
	zipFile(path1, zippath=zippath1, password="")
	zipFile(path2, zippath=zippath2, password="")
	zipFile(path1, zippath=zippath3, password=PASSWORD)
	print("压缩完成，正在上传")
	return zippath0, zippath1, zippath2

	
@timer
def upload(zippath0, zippath1, zippath2):
	uploadFile(zippath0, "合集/合集")
	uploadFile(zippath1, "合集/简体版")
	uploadFile(zippath2, "合集/繁體版")
	print("上传完成")
	
	
def main(path=""):
	if not path:
		path = os.getcwd()
	os.chdir(path)  # 更改工作路径
	print(f"当前路径：{path}")
	
	removeFiles()
	files = findFile(path, ".docx", ".txt")
	convertFiles(files)
	# common = os.path.commonpath(files)
	# print(f"{common=}")
	path0, path1, path2 = makeZipFile(os.path.commonpath(files))
	upload(path0, path1, path2)


if __name__ == '__main__':
	path = r"D:\Download\Browser\小说"
	# if os.path.exists(path):
	# 	removeFile(path)
	if not os.path.exists(path):
		downloadFiles(os.path.dirname(path))
	main(path) # 指定路径方能使用
	