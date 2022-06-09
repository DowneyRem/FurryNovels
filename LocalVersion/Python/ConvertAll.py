#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from FileOperate import findFile, openDocx, openText, saveText, removeFile, monthNow, openNowDir
from Language import getLanguage
from config import cc1, cc2


def setPath(path):
	path0 = path.replace("\小说推荐", "\兽人小说\小说推荐\频道版")
	path0 = path0.replace(".docx", ".txt")
	
	dirandfile = path0.replace(sharepath + "\频道版", "")
	path1 = os.path.join(sharepath + "\简体版" + cc1.convert(dirandfile))  # 简体目录
	path2 = os.path.join(sharepath + "\繁體版" + cc2.convert(dirandfile))  # 繁体目录
	
	(filepath, name) = os.path.split(path)  # 分离文件名和目录名
	name = os.path.splitext(name)[0]
	text = "{}\n{}\n{}\n{}".format(path0, path1, path2, name)
	# print(text)
	return path0, path1, path2, name


def openFile(path):
	(dir, name) = os.path.split(path)
	(name, ext) = os.path.splitext(name)
	if ext == ".docx":
		text = openDocx(path)
	elif ext == ".txt":
		text = openText(path)
	return text


def convertText(path):
	text = openFile(path)
	(path0, path1, path2, name) = setPath(path)
	saveText(path0, text)  # 不区分繁简，存频道目录
	
	language = getLanguage(text)
	if   language == "#zh_tw":
		saveText(path2, text)      # 复制后，存繁体目录
		text1 = cc1.convert(text)  # 繁体文件，转简体
		saveText(path1, text1)     # 转简体，存简体目录
	elif language == "#zh_cn":
		saveText(path1, text)      # 复制后，存简体目录
		text2 = cc2.convert(text)  # 简体文件，转繁体
		saveText(path2, text2)     # 转繁体，存繁体目录
	

def convert(pathlist):
	for i in range(0, len(pathlist)):
		filepath = pathlist[i]
		path0, path1, path2, name = setPath(filepath)
		if not os.path.exists(path0):
			convertText(filepath)
			rate = round(100 * i / len(pathlist))
			print("【{}】已转换，当前进度{}%".format(name, rate))
		elif os.path.exists(path0):
			# print("【{}】已存在".format(name))
			pass


def getPath(path):
	li = "备用 待整理 新建文件夹 工具".split(" ")
	list1 = findFile(path, ".docx", ".txt")
	list2 = list.copy(list1)
	for i in range(0, len(list1)):
		filepath = list1[i]
		k = 0
		for j in range(len(li)):  # 不处理的文件夹
			a = "\\{}\\".format(li[j])
			if a in filepath:
				k += 1
		if k >= 1:
			list2.remove(filepath)
	convert(list2)


def main():
	print("是否要【删除旧文件】重新转换？")
	string = input("输入【 1 】即【删除旧文件】" + "\n" * 2)
	if str(1) in string:
		removeFile(sharepath)
		print("【删除】旧文件")
	else:
		print("【保留】旧文件")
	
	print("文档转换开始：")
	getPath(path)
	print("文档转换已完成")
	os.system("python ./PrintTags.py")
	os.system("pause")


if __name__ == "__main__":
	path = os.getcwd()
	path = path.replace("\工具", "")
	sharepath = path.replace("\小说推荐", "\兽人小说\小说推荐")
	main()
