#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import shutil
import zipfile
from functools import wraps

if "小说推荐" in os.getcwd():
	from docx.api import Document
	from win32com.client import DispatchEx


def timethis(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		r = func(*args, **kwargs)
		end = time.perf_counter()
		print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
		return r
	return wrapper


pathlist = []
def findFile(path, *extnames):
	## 省略 extnames 参数可以获取全部文件
	for dir in os.listdir(path):
		dir = os.path.join(path, dir)
		if os.path.isdir(dir):
			findFile(dir, *extnames)
			
		if os.path.isfile(dir):
			if len(extnames) > 0 :
				for extname in extnames:
					(name, ext) = os.path.splitext(dir)
					if ext == extname:
						pathlist.append(dir)
			elif len(extnames) == 0 :
				pathlist.append(dir)
	return pathlist


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


def openText4(path):
	textlist = []
	try:
		with open(path, "r", encoding="UTF8") as f:
			textlist = f.readlines()[0:4]
	except UnicodeError:
		try:
			with open(path, "r", encoding="GBK") as f:
				textlist = f.readlines()[0:4]
		except UnicodeError:
			with open(path, "r", encoding="BIG5") as f:
				textlist = f.readlines()[0:4]
	finally:
		return textlist


def openDocx(path):
	try:
		docx = Document(path)
		text = ""
		for para in docx.paragraphs:
			if para.style.name == "Normal Indent":  # 正文缩进
				text += "　　" + para.text + "\n"
			else:
				text += para.text + "\n"  # 除正文缩进外的其他所有
		return text
	except IOError:
		print("文件打开失败")
		
		
def openDocx4(path):
	try:
		docx = Document(path)
		text = "" ; j = 1
		for para in docx.paragraphs:
			if j < 5:  # 只读取前4行内容
				j += 1
				if para.style.name == "Normal Indent":  # 正文缩进
					text += "　　" + para.text + "\n\t"
				else:
					text += "" + para.text + "\n\t"  # 除正文缩进外的其他所有
			else:
				break
		textlist = text.split("\t")  #保留行尾换行符
		return textlist
	except IOError:
		print("文件打开失败")


def openExcel(path):  #打开软件手动操作
	excel = DispatchEx('Excel.Application')  # 独立进程
	excel.Visible = 1  # 0为后台运行
	excel.DisplayAlerts = 0  # 不显示，不警告
	xlsx = excel.Workbooks.Open(path)  # 打开文档


#暂未加入保存函数内，如何加入？
def formatFileName(text):
	list = '/ \ : * " < > | ?'.split(" ")
	for i in range(len(list)):
		a = list[i]
		text = text.replace(a, " ")
	return text


def saveDocx(path, text):
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	if not os.path.exists(dir):
		os.makedirs(dir)
	
	word = DispatchEx('Word.Application')  # 独立进程
	word.Visible = 0  # 0为后台运行
	word.DisplayAlerts = 0  # 不显示，不警告
	template = "D:\\Users\\Administrator\\Documents\\自定义 Office 模板\\小说.dotm"
	docx = word.Documents.Add(template)  # 创建新的word文档
	
	s = word.Selection
	s.Text = text  # 写入文本
	docx.Application.Run("小说排版")  # 运行宏
	
	docx.SaveAs2(path, 16)   # 保存文档并退出word
	# print("【" + name + "】已保存")
	docx.Close(True)
	word.Quit()


def saveText(path, text):
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	name = name.replace(".txt", "")
	if not os.path.exists(dir):
		os.makedirs(dir)
	try:
		with open(path, "w", encoding="UTF8") as f:
			f.write(text)
		# print("【" + name + "】保存成功")
	except IOError:
		print("【" + name + "】保存失败")


#for循环内部，使用a+模式，写入测试文件
def saveTextDesktop(name, text):
	path = "D:\\Users\\Administrator\\Desktop"
	path = os.path.join(path, name)
	try:
		with open(path, "a+", encoding="UTF8") as f:
			f.write(text)
		# print("【" + name + "】保存成功")
	except IOError:
		print("【" + name + "】保存失败")


def saveCsv(path, text):
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	if not os.path.exists(dir):
		os.makedirs(dir)
	try:
		with open(path, "w", encoding="UTF-8-sig") as f:
			f.write(text)
		print("已存为：" + name)
	except IOError:
		print("保存失败")


def makeDirs(path):
	if not os.path.exists(path):
		os.makedirs(path)


def removeFile(path):
	if os.path.isdir(path):
	# if os.path.exists(path):
		shutil.rmtree(path)
		os.makedirs(path)
	if os.path.isfile(path):
		os.remove(path)
	

def monthNow():
	year = str(time.localtime()[0])
	month = str(time.localtime()[1])
	if len(month) == 1:
		month = "0" + month
	string = os.path.join(year, month)
	return string


def openNowDir():
	path = os.getcwd()
	path = path.replace("\小说推荐\工具", "\兽人小说\小说推荐\频道版")
	text = monthNow()
	pathNow = os.path.join(path, text)
	if os.path.exists(pathNow):
		os.system('start explorer '+ pathNow)
	else:
		os.system('start explorer '+ path)
		
		
def zipFile(path, delete=1):
	# 传入某文件或文件夹路径后，将其所在文件夹打包压缩
	# delete 为0或为""时，压缩后删除源文件
	
	if os.path.isdir(path):
		dir = path    #文件上级文件夹
	elif os.path.isfile(path):
		(dir, name) = os.path.split(path)
	else:
		print("不存在 {}".format(path))
		os._exit(0)
		
	zippath = os.path.join(dir + ".zip")
	if os.path.exists(zippath):
		os.remove(zippath) #重新压缩
		
	list = findFile(dir, ) ## 获取目录下所有文件
	z = zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED)
	for i in range(len(list)):
		path = list[i]
		(filedir, name) = os.path.split(path)
		filedir = filedir.replace(dir, "")
		filedir = os.path.join(filedir, name)
		# print(filedir)
		z.write(filename=path, arcname=filedir)   #压缩的文件，zip内路径
	z.close()
	
	if delete == 0 or delete == "":
		try:
			shutil.rmtree(dir)   #删除文件夹
			print("【已经删除zip的源文件夹】")
		except IOError:
			print("【zip的源文件夹删除失败】")
			
	zipname = os.path.split(zippath)[1]
	print("【{}】压缩完成".format(zipname))
	return zippath


def unzipFile(path, delete=1):
	# 传入zip后，解压至以zip文件名建立的新文件夹
	# delete 为0或为""时，解压后删除源文件
	name = os.path.split(path)[1]
	dir = os.path.splitext(path)[0]   # 解压后的文件夹
	if os.path.exists(dir):
		removeFile(dir)
	
	if not zipfile.is_zipfile(path):
		print("【{}】不存在或不是zip文件".format(name))
		
	else:
		z = zipfile.ZipFile(path, "r")
		for file in z.namelist():
			z.extract(file, dir)
		z.close()
		print("【{}】已经完成解压".format(name))
		
		if delete == 0 or delete == "":
			try:
				removeFile(path)  #删除zip文件
				print("【{}】已经删除".format(name))
			except UnicodeError:
				print("【{}】删除失败".format(name))
	return dir


if __name__ == '__main__':
	pass
