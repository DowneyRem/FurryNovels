#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import shutil
import logging
# import zipfile as zf
import pyzipper as zf
from functools import wraps
from platform import platform

if "Windows" in platform():
	import winreg
	if "小说推荐" in os.getcwd():
		from docx.api import Document
		from win32com.client import Dispatch, DispatchEx


def timethis(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		r = func(*args, **kwargs)
		end = time.perf_counter()
		print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
		return r
	return wrapper


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


def saveFileCheck(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		arg = args[0]
		(dir, name) = os.path.split(arg)  # 分离文件名和目录名
		if not os.path.exists(dir):
			os.makedirs(dir)
		r = func(*args, **kwargs)
		return r
	return wrapper


# 暂未加入保存函数内，如何加入？
def formatFileName(text):
	list = '/ \ : * " < > | ? &lt; &gt; &&amp; &quot; &apos; &nbsp;'.split(" ")
	for i in range(len(list)):
		a = list[i]
		text = text.replace(a, " ")
	return text


pathlist = []
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


@openFileCheck
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


@openFileCheck
def openTextLines(path):
	textlist = []
	try:
		with open(path, "r", encoding="UTF8") as f:
			textlist = f.readlines()
	except UnicodeError:
		try:
			with open(path, "r", encoding="GBK") as f:
				textlist = f.readlines()
		except UnicodeError:
			with open(path, "r", encoding="BIG5") as f:
				textlist = f.readlines()
	finally:
		return textlist


@openFileCheck
def openDocx(path):
	docx = Document(path)
	text = ""
	for para in docx.paragraphs:
		if para.style.name == "Normal Indent":  # 正文缩进
			text += "　　" + para.text + "\n"
		else:
			text += para.text + "\n"  # 除正文缩进外的其他所有
	return text


@openFileCheck
def openDocx4(path):
	docx = Document(path)
	text = ""; j = 1
	for para in docx.paragraphs:
		if j < 5:  # 只读取前4行内容
			j += 1
			if para.style.name == "Normal Indent":  # 正文缩进
				text += "　　" + para.text + "\n\t"
			else:
				text += "" + para.text + "\n\t"  # 除正文缩进外的其他所有
		else:
			break
	textlist = text.split("\t")  # 保留行尾换行符
	return textlist


@openFileCheck
def openExcel(path):  # 打开软件手动操作
	excel = DispatchEx('Excel.Application')  # 独立进程
	excel.Visible = 1  # 0为后台运行
	excel.DisplayAlerts = 0  # 不显示，不警告
	xlsx = excel.Workbooks.Open(path)  # 打开文档
	print("打开Excel……")


def getFileTime(path):
	time1 = os.path.getctime(path)  # 文件创建日期，返回时间戳
	time2 = os.path.getmtime(path)  # 文件最近修改时间
	time3 = os.path.getatime(path)  # 文件最近访问时间
	timelist = [time1, time2, time3]
	return timelist


@saveFileCheck
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
	
	docx.SaveAs2(path, 16)  # 保存文档并退出word
	print("已保存：【{}】".format(name))
	docx.Close(True)
	word.Quit()


@saveFileCheck
def saveText(path, text):
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	if not os.path.exists(dir):
		os.makedirs(dir)
	if not path.endswith(".txt"):
		path += ".txt"
	try:
		with open(path, "w", encoding="UTF8") as f:
			f.write(text)
		# print("已保存：【{}】".format(name))
	except IOError:
		print("保存失败：【{}】".format(name))


def saveTextDesktop(name, text):
	# for循环内部，使用a+模式，写入测试文件
	path = desktop()
	path = os.path.join(path, name)
	try:
		with open(path, "a+", encoding="UTF8") as f:
			f.write(text)
		# print("已保存：【{}】".format(name))
	except IOError:
		print("保存失败：【{}】".format(name))


@saveFileCheck
def saveCsv(path, text):
	(dir, name) = os.path.split(path)  # 分离文件名和目录名
	if not os.path.exists(dir):
		os.makedirs(dir)
	try:
		with open(path, "w", encoding="UTF-8-sig") as f:
			f.write(text)
	# print("已保存为：【{}】".format(name))
	except IOError:
		print("保存失败：【{}】".format(name))


def desktop():
	if "Windows" in platform():  # 其他平台我也没用过
		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
							 r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
		return winreg.QueryValueEx(key, "Desktop")[0]


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
		os.system('start explorer ' + pathNow)
	else:
		os.system('start explorer ' + path)


def makeDirs(path):
	if not os.path.exists(path):
		os.makedirs(path)


def removeFile(path):
	if os.path.isdir(path):
		try:
			shutil.rmtree(path)
			logging.info("【{}】已经删除".format(path))
		except IOError:
			print("【{}】删除失败".format(path))
	# os.makedirs(path)
	
	if os.path.isfile(path):
		name = os.path.split(path)[1]
		try:
			os.remove(path)
			# logging.info("【{}】已经删除".format(name))
			print("【{}】已经删除".format(name))
		except IOError:
			print("【{}】删除失败".format(name))


@timethis
def zipFile(path, password="", delete=0):
	# 使用 pyzipper ，可用aes256加密，压缩传入的文件或文件夹
	# parm delete 不为0时，压缩后删除源文件
	
	def zipSingleFile(path, zippath, password):
		if password: encryption=zf.WZ_AES
		else: encryption = None
		with zf.AESZipFile(zippath, 'w', compression=zf.ZIP_LZMA, encryption=encryption) as z:
		# with zf.ZipFile(zippath, 'w', compression=zf.ZIP_DEFLATED) as z:
			z.setpassword(password.encode(encoding="utf-8"))
			name = os.path.split(path)[1]
			z.write(filename=path, arcname=name)  # 压缩的文件，zip内路径
	
	
	def zipFolder(path, zippath, password):
		list = findFile(path, )  # 获取目录下所有文件
		if password: encryption=zf.WZ_AES
		else: encryption = None
		with zf.AESZipFile(zippath, 'w', compression=zf.ZIP_LZMA, encryption=encryption) as z:
			# with zf.ZipFile(zippath, 'w', compression=zf.ZIP_DEFLATED) as z:
			z.setpassword(password.encode(encoding="utf-8"))
			for i in range(len(list)):
				filepath = list[i]
				arcname = filepath.replace(path, "")
				z.write(filename=filepath, arcname=arcname)  # 压缩的文件，zip内路径
	
	
	if os.path.isdir(path):
		zipfilepath = "{}.zip".format(path)
		removeFile(zipfilepath)
		zipFolder(path, zipfilepath, password)
		
	elif os.path.isfile(path):
		filename = os.path.splitext(path)[0]
		zipfilepath = "{}.zip".format(filename)
		removeFile(zipfilepath)
		zipSingleFile(path, zipfilepath, password)
		
	else:
		print("不存在 {}".format(path))
		os._exit(0)
		
	if delete != 0:
		removeFile(path)

	zipname = os.path.split(zipfilepath)[1]
	print("【{}】压缩完成".format(zipname))
	# print(zipfilepath)
	return zipfilepath


# @timethis
def unzipFile(path, password="", mode=0, delete=0):
	# 使用 pyzipper 可解压加密的zip文件（ase256 与 ZipCrypto）,前者会快得多
	# 智能解压：path传入zip路径解压zip，传入文件夹则解压其路径下的zip
	# 智能解压：zip内无文件夹则会新建以zip文件名为名的文件夹，zip只有单文件不新建文件夹
	# mode==1 ，解压zip内部的zip文件
	# delete==1 ，解压后删除zip源文件；同时mode==1，解压后会删除所有zip
	# 软件压缩设置：勾选zip使用Unicode文件名，避免解压后文件名乱码
	
	if os.path.isdir(path):
		ziplist = findFile(path, ".zip")
		if len(ziplist) == 0:
			print("{}目录下无zip文件".format(path))
		for zipfile in ziplist:
			unzipFile(zipfile, password, mode=mode, delete=delete)
		
	elif zf.is_zipfile(path):
		name = os.path.split(path)[1]
		dir = os.path.splitext(path)[0]
		if os.path.exists(dir):
			removeFile(dir)
		
		with zf.AESZipFile(path, "r") as z:
		# with zf.ZipFile(path, "r") as z:
			if z.namelist()[0].endswith("/"): 	# 内有文件夹，直接解压
				dir = os.path.split(path)[0]
				directory = os.path.join(dir, z.namelist()[0])
				removeFile(directory)
			elif len(z.namelist()) == 1:        # 单文件不新建文件夹
				dir = os.path.split(path)[0]
			else:                               # 多文件，新建文件夹
				dir = os.path.splitext(path)[0]
				
			comment = z.comment.decode(encoding="utf-8")
			if comment:
				print("压缩文件注释:{}".format(comment))
			
			try:
				logging.info("【{}】解压中……".format(name))
				# z.extractall(dir, members=z.namelist(), pwd=password.encode('utf-8'))
				for file in z.namelist():
					z.extract(file, dir, password.encode('utf-8'))
					if file.endswith(".zip") and mode:  # 解压zip内的zip
						path = os.path.join(dir, file)
						unzipFile(path, password, mode=mode, delete=delete)
						
				print("【{}】已经完成解压".format(name))
			except RuntimeError:
				print("密码【{}】错误，解压失败".format(password))
		
		if delete != 0:
			removeFile(path)  # 删除zip文件
		return dir
	

def main():
	pass


if __name__ == '__main__':
	pass
