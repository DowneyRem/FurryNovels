#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
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


def findtext(path):
	for dir in os.listdir(path):
		dir = os.path.join(path, dir)
		if os.path.isdir(dir):
			findtext(dir)
		if os.path.isfile(dir):
			(name, ext) = os.path.splitext(dir)
			if ext == ".txt" or ext == ".TXT":
				list.append(dir)
	return list


def removefile(list):
	for i in range(0 ,len(list)):
		path = list[i]
		(filepath, name) = os.path.split(path)  # 分离文件名和目录名
		(name, ext) = os.path.splitext(name)
		
		if os.path.exists(path):
			try:
				os.remove(path)
				print("【" + name + "】删除成功")
			except IOError:
				print("【" + name + "】删除失败")


def finddirs(path):
	for dir in os.listdir(path):
		dir = os.path.join(path, dir)
		list1.append(dir)
		if os.path.isdir(dir):
			finddirs(dir)
		if os.path.isfile(dir):
			list2.append(dir)
	return (list1, list2)


def removedirs(list, list2):
	for i in range(0 ,len(list1)):
		path = list[i]
		name = path
		
		(list1, list2) = finddirs(path)
		if len(list2) == 0:
			try:
				os.removedirs(path)
				print("【" + name + "】删除成功")
			except OSError:
				print("")



def main():
	print("删除TXT开始：")
	print("下列文件已被删除：")
	print("————————————————")
	
	findtext(path1)
	removefile(list)
	findtext(path2)
	removefile(list)
	
	
	# finddirs(path1)
	# removedirs(list)
	# finddirs(path2)
	# removedirs(list)
	
	
	print("————————————————")
	# os.system("pause")


if __name__ == '__main__':
	path = os.path.join(os.getcwd())
	path = path.replace("\小说推荐\工具", "")
	path1 = os.path.join(path + "\兽人小说\小说转换版")
	path2 = os.path.join(path + "\兽人小说\小说推荐")
	
	list = [] ; text = ""; main()
