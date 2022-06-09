#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os, shutil
import re
from decimal import Decimal
from datetime import datetime
from functools import cmp_to_key, wraps
# from FileOperate import findFile, openText, saveText
# from ChineseNum import trans, strNum


pyfilever = 1.2
pathlist = []
dict1 = {
	"shu": {'一': 1, "两": 2, '二': 2, '三': 3, '四': 4, '五': 5,
	        '六': 6, '七': 7, '八': 8, '九': 9, "〇": 0, "零": 0, },
	"wei": {"dian": "点", "shi": "十", "bai": "百",
	        "qian": "千", "wan": "万", "yi": "亿"}}


# 数字转换部分，可由 ChineseNum 导入
def transSerial(s: str, numdict: dict = dict1):
	# 序号转换，小数转换半成品
	shu = numdict["shu"]
	j = ""
	for i in s:
		j += str(shu[i])
	return int(j)


def trans(s: str, numdict=dict1) -> int:
	# 万位以下中文数字转换：九千零二十一 -> 9021
	# 参考自：https://segmentfault.com/a/1190000013048884
	
	shu = numdict["shu"]
	wei = numdict["wei"]
	num = 0
	dian, shi, bai, qian, wan, yi = wei["dian"], wei["shi"], wei["bai"], wei["qian"], wei["wan"], wei["yi"]
	dian, shi, bai, qian, wan, yi = s.find(dian), s.find(shi), s.find(bai), s.find(qian), s.rfind(wan), s.rfind(yi)
	
	if wan != -1 or yi != -1:
		try:
			raise ValueError("数字过大")
		except ValueError as e:
			print("{}，请使用transBigNum".format(e))
	
	else:
		if qian != -1:
			num += shu[s[qian - 1: qian]] * 1000
		if bai != -1:
			num += shu[s[bai - 1: bai]] * 100
		if shi != -1:
			shiwei = s[shi - 1: shi].replace("零", "")
			num += shu.get(shiwei, 1) * 10  # 处理十位忽略的一
		
		if dian != -1:
			try:
				num += shu[s[dian - 1: dian - 0]]
			except KeyError:  # 十
				num += 10
			xiaoshu = s[dian + 1:]
			num += transSerial(xiaoshu) / 10 ** len(xiaoshu)
		
		elif s[-1] in shu:
			num += shu[s[-1]]
		
		# print(num)
		return num


def strSerial(num: float, numdict=dict1) -> str:
	# 序号转换，小数转换半成品
	shu = numdict["shu"]
	wei = numdict["wei"]
	shu = dict(zip(shu.values(), shu.keys()))
	
	text = ""
	for i in str(num):
		try:
			i = shu[int(i)]
		except ValueError:  # 小数点报错
			i = wei["dian"]
		text += i
	# print(text)
	return text


def strNum(num: float, numdict=dict1) -> str:
	shu = numdict["shu"]
	wei = numdict["wei"]
	shu = dict(zip(shu.values(), shu.keys()))
	l = list(wei.values())
	
	text = ""
	strnum = str(int(num))
	length = len(strnum)
	if length <= 4:
		for i in range(len(strnum)):
			if shu[int(strnum[i])] != "零":
				j = shu[int(strnum[i])] + l[length - i - 1]
				text += j
			else:
				text += "零"
		
		# 去除多个连续占位的零，去除末尾的零
		text = re.sub("零{2,}", "零", text, 1)
		if text.endswith("零"):
			text = text[:-1]
		text = text.replace("点", "")
		
		if num != int(num):  # 小数部分
			decimalnum = Decimal(str(num)) - int(num)
			decimalnum = str(decimalnum)[2:]
			text += wei["dian"] + strSerial(int(decimalnum))
		
		# print(text)
		return text


# 文件处理部分
def findFile(path, *extnames):
	# 省略 extnames 参数可以获取全部文件
	for dir in os.listdir(path):
		dir = os.path.join(path, dir)
		if os.path.isdir(dir):
			findFile(dir, *extnames)
		
		if os.path.isfile(dir):
			if len(extnames) > 0:
				for extname in extnames:
					(name, ext) = os.path.splitext(dir)
					if ext == extname:
						pathlist.append(dir)
			elif len(extnames) == 0:
				pathlist.append(dir)
	return pathlist


def openFileCheck(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		arg = args[0]
		if os.path.exists(arg):
			try:
				r = func(*args, **kwargs)
				return r
			except IOError:
				print("文件被占用：{}".format(arg))
		else:
			print("文件不存在：{}".format(arg))
	return wrapper


@openFileCheck
def openText(path):
	text = ""
	try:
		with open(path, "r", encoding="UTF8") as f:
			text = f.read()
	except UnicodeError:
		try:
			with open(path, "r", encoding="GBK") as f:
				text = f.read()
		except UnicodeError:  # Big5 似乎有奇怪的bug，不过目前似乎遇不到
			with open(path, "r", encoding="BIG5") as f:
				text = f.read()
	finally:
		return text


def saveText(path, text):
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	if not os.path.exists(dir):
		os.makedirs(dir)
	try:
		with open(path, "w", encoding="UTF8") as f:
			f.write(text)
	# print("已保存：【{}】".format(name))
	except IOError:
		print("保存失败：【{}】".format(name))


# 核心功能
def createText(num, mode=0, delete=0):
	if delete:
		try:
			shutil.rmtree(folder)
		except Exception as e:
			print("".format(e))
			
	for i in range(num):
		if mode == 0:
			name = "第{}章".format(i + 1)
		else:
			name = "第{}章".format(strNum(i + 1))
		path = os.path.join(folder, name + ".txt")
		saveText(path, name)


def cmp(a, b):
	def getNum(a):
		a = os.path.split(a)[1]
		pattern = "[一二三四五六七八九零〇点十百千万亿]{1,}"
		if re.findall(pattern, a):
			a = re.findall(pattern, a)
			a = trans(a[0])
		else:
			try:
				a = re.findall("[0-9.]{1,}", a)
				a = float(a[0])
			except Exception as e:
				print(e)
		return a
	
	a, b = getNum(a), getNum(b)
	if a > b:
		return 1
	elif a < b:
		return -1
	else:
		return 0


def mergeText(folder=os.getcwd()):
	l = findFile(folder, ".txt")
	l.sort(key=cmp_to_key(cmp))
	
	name = os.path.split(folder)[1]
	time = str(datetime.today())[:-7]
	pyfile = os.path.split(__file__)[1]
	info = "本文采用 {} ver{} 合并，合并时间：{}".format(pyfile, pyfilever, time)
	print(info)
	
	text = "{}\n".format(name, info)
	print("开始合并TXT，顺序如下：{}{}".format("\n","-"*30))
	for file in l:
		text += openText(file) + "\n"*3
		file = file.replace("{}\\".format(folder), "")
		print(file)
	print("{}".format("-" * 30))
	textpath = "{}.txt".format(folder)
	
	try:
		saveText(textpath, text)
		print("合并成功：{}.txt\n文件路径：{}".format(name, textpath))
	except Exception as e:
		print("".format(e))
		

if __name__ == '__main__':
	if "FurryNovelsBot" in os.getcwd():
		folder = os.path.join(os.getcwd(), "ceui")	
		createText(12, 1)
	else:
		folder = os.path.join(os.getcwd())
		
	print("当前路径：{}".format(folder))
	mergeText(folder)
