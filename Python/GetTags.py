#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from DictText import textdict, cmp2
from functools import cmp_to_key
from FileOperate import findFile, openDocx

from opencc import OpenCC
cc1 = OpenCC('tw2sp')  #繁转简
cc2 = OpenCC('s2twp')  #簡轉繁

import time
from functools import wraps


def timethis(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		r = func(*args, **kwargs)
		end = time.perf_counter()
		print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
		return r
	return wrapper


def sortTags(set, cmp):  # 按dict内顺序对转换后的标签排序
	text = ""
	li = list(set)
	li.sort(key=cmp_to_key(cmp))
	for i in range(len(li)):
		tag = li[i]
		text += "#" + tag + " "
	return text


def saveText(text):
	path = "D:\\Users\\Administrator\\Desktop\\1.txt"
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	name = name.replace(".txt", "")
	if not os.path.exists(dir):
		os.makedirs(dir)
	try:
		with open(path, "a+", encoding="UTF8") as f:
			f.write(text)
		# print("【" + name + "】保存成功")
	except IOError:
		print("【" + name + "】保存失败")


def getTags(text):  #获取不靠谱的标签
	string = ""
	s1 = set() ; s2 = set()
	list1 = list(textdict.keys())
	list2 = list(textdict.values())
	for i in range(0, len(list1)):
		a = list1[i]
		num = text.count(a)
		if num > 0:
			b = list2[i]
			# print((a, b, num))
			string += a +","+ b +","+ str(num) +"\n"
		if num > 5:
			s1.add(list1[i])  #汉字标签
			s2.add(list2[i])  #英文标签
	
	saveText(string)
	s1 =sortTags(s1, cmp2)
	s2 =sortTags(s2, cmp2)
	print("可能存在的标签：")
	print(s1)
	print(s2)
	print("\n"*2)
	return s1, s2

def getText(path):
	list1 = findFile(path, ".docx")
	for i in range(len(list1)):
		path = list1[i]
		(dir, name) = os.path.split(path)
		print(name)
		text = openDocx(path)
		text = cc1.convert(text)  #转简体，只处理简体标签
		getTags(text)


if __name__ == '__main__':
	path = os.getcwd()
	path = path.replace("\工具", "")
	path = os.path.join(path, "2022\\03")
	print(path)
	getText(path)
