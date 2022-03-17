#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
from docx.api import Document
from docx import RT
from functools import wraps


def timethis(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		r = func(*args, **kwargs)
		end = time.perf_counter()
		print("{}.{} : {}".format(func.__module__, func.__name__, end - start))
		return r
	return wrapper


def monthnow():
	year = str(time.localtime()[0])
	month = str(time.localtime()[1])
	if len(month) == 1:
		month = "0" + month
	string = os.path.join(year, month)
	return string

def opennowdir(path):
	path = path.replace("\小说推荐", "\兽人小说\小说推荐\频道版")
	text = monthnow()
	path = os.path.join(path,text)
	os.system('start explorer '+ path)


def findfile(path):
	for dir in os.listdir(path):
		dir = os.path.join(path, dir)
		if os.path.isdir(dir):
			findfile(dir)
		if os.path.isfile(dir):
			(name, ext) = os.path.splitext(dir)
			if ext == ".docx":
				list.append(dir)
	return list


def opendocx(path):
	docx = Document(path)
	text = ""
	for para in docx.paragraphs:
		if para.style.name == "Normal Indent":  # 正文缩进
			text += "　　" + para.text + "\n"
		else:
			text += para.text + "\n"  # 除正文缩进外的其他所有
	return text


def savetext(path, text):
	(dir, name) = os.path.split(path) #分离文件名和目录名
	if not os.path.exists(dir):
		os.makedirs(dir)
	with open(path, "w", encoding = "UTF8") as f:
		f.write(text)


def docx2txt(list):
	for i in range(0, len(list)):
		path = list[i]
		textpath = path.replace("\小说推荐", "\兽人小说\小说推荐\频道版")
		textpath = textpath.replace(".docx", ".txt")
		(filepath, name) = os.path.split(path)  # 分离文件名和目录名
		name = name.replace(".docx", "")
		
		if os.path.exists(textpath):
			i += 1
			# print("【" + name + "】在程序运行前已转换")
		else:
			try:
				text = opendocx(path)
				savetext(textpath, text)
				print("【" + name + "】转换成功，当前进度：" + str(round(100 *(i+1)/len(list),2))+"%")
	
			except:
				print("【" + name + "】打开失败或文件有问题")



def main():
	print("docx 转 txt ：")
	print("————————————————")
	
	path = os.getcwd()
	path = path.replace("\工具","")
	findfile(path)
	docx2txt(list)
	opennowdir(path)
	

if __name__ == "__main__":
	list = []
	main()
