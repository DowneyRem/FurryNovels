#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
from opencc import OpenCC
from functools import wraps
cc1 = OpenCC('tw2sp')  #繁转简
cc2 = OpenCC('s2twp')  #简转繁


def timethis(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		r = func(*args, **kwargs)
		end = time.perf_counter()
		print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
		return r
	
	return wrapper


def findfile(path):
	for dir in os.listdir(path):
		dir = os.path.join(path, dir)
		if os.path.isdir(dir):
			findfile(dir)
		if os.path.isfile(dir):
			(name, ext) = os.path.splitext(dir)
			if ext == ".txt":
				pathlist.append(dir)
	return pathlist


def opentext(path):
	text = ""
	try:
		with open(path,"r", encoding = "UTF8") as f:
			text = f.read()
	except UnicodeError:
		try:
			with open(path,"r", encoding = "GBK") as f:
				text = f.read()
		except UnicodeError: #Big5 似乎有奇怪的bug，不过目前似乎遇不到
			with open(path,"r", encoding = "BIG5") as f:
				text = f.read()
	finally:
		return text
	
	
def opendocx(path):
	docx = Document(path)
	text = ""
	for para in docx.paragraphs:
		if para.style.name == "Normal Indent":  # 正文缩进
			text += "　　" + para.text + "\n"
		else:
			text += para.text + "\n"  # 除正文缩进外的其他所有
	print(text)
	return text


def makedirs(path):
	if not os.path.exists(path):
		os.makedirs(path)


def savetext(path, text):
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	name = name.replace(".txt", "")
	
	if not os.path.exists(dir):
		os.makedirs(dir)
	try:
		with open(path, "w", encoding="UTF8") as f:
			f.write(text)
	except IOError:
		print("【" + name + "】转换失败")
		
		
def convert(list):
	num = len(pathlist)
	for i in range(num):
		path = pathlist[i]
		dirandfile = path.replace(path0, "")
		path11 = os.path.join(path1 + cc1.convert(dirandfile))  #简体目录
		path22 = os.path.join(path2 + cc2.convert(dirandfile)) #繁体目录
		name = os.path.split(path)[1].replace(".txt", "")
		
		if os.path.exists(path11) and os.path.exists(path22):
			i += 1
			# print("【" + name + "】在程序运行前已转换")
		else:
			text = opentext(path)
			text1 = cc1.convert(text)  #转简体
			text2 = cc2.convert(text)  #转繁体
			
			if "會"in text or "後"in text or "來"in text or "東"in text or "電"in text or "個"in text:
				savetext(path22, text)   #繁体文件复制一份，存繁体目录
				savetext(path11, text1)  #繁体文件转换过后，存简体目录
		
			elif "会"in text or "来"in text or "东"in text or "电"in text or "个"in text:
				savetext(path11, text)   #简体文件复制一份，存简体目录
				savetext(path22, text2)  #简体文件转换过后，存繁体目录
			
			print("【"+ name +"】转换完成，当前进度：" + str(round(100*(i+1)/num,2))+"%")
		

def main():
	print("繁简转换开始：")
	print("下列文件已完成转换：")
	print("————————————————")
	findfile(path0)
	
	if len(pathlist) == 0:
		print("————————————————")
		print("没有可转换的文件")
		os.system("pause")
	
	else:
		convert(list)
		print("————————————————")
		print("所有文件均完成转换")
	# os.system("pause")

if __name__ == '__main__':
	path = os.path.join(os.getcwd())
	path = path.replace("\小说推荐\工具", "\兽人小说\小说推荐")
	path0 = os.path.join(path + "\频道版")
	path1 = os.path.join(path + "\简体版")
	path2 = os.path.join(path + "\繁體版")

	pathlist = []
	main()
