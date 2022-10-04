#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import json
import time
import shutil
import logging
import webbrowser
from functools import wraps
from platform import platform

# import zipfile as zf
import pyzipper as zf
from docx import Document  # 使用 docx-hitalent
# from docx.shared import Pt

if "Windows" in platform():
	import winreg
	from win32com.client import Dispatch, DispatchEx
	
	
template_dotm = r"D:\Users\Administrator\Documents\自定义 Office 模板\小说.dotm"
template_dotx = r"D:\Users\Administrator\Documents\自定义 Office 模板\模板.docx"


def timer(function):
	@wraps(function)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		result = function(*args, **kwargs)
		end = time.perf_counter()
		print(f"{function.__module__}.{function.__name__}: {end - start}")
		return result
	return wrapper


def openFileCheck(function):
	@wraps(function)
	def wrapper(*args, **kwargs):
		arg = args[0]
		if os.path.exists(arg):
			try:
				result = function(*args, **kwargs)
				return result
			except IOError:
				print(f"文件被占用：{arg}")
		else:
			print(f"文件不存在：{arg}")
	return wrapper


def saveFileCheck(function):
	@wraps(function)
	def wrapper(*args, **kwargs):
		path = args[0]
		(dir, name) = os.path.split(path)
		if not os.path.exists(dir):
			os.makedirs(dir)
		name = formatFileName(name)
		path = os.path.join(dir, name)
		result = function(path, *args[1:], **kwargs)
		return result
	return wrapper


# 已通过@saveFileCheck加入保存文件的函数内
def formatFileName(text) -> str:
	if text:
		text = re.sub('[\/:*?"<>|]', ' ', text)
		text = text.replace('  ', '')
		return text
	else:
		return ""
	

def findFile(path, *extnames) -> list:
	# 省略 extnames 参数可以获取全部文件
	# extname="" 获取无后缀名文件
	pathlist = []
	for root, dirs, files in os.walk(path):
		# print(root, dirs, files, sep="\n")
		for file in files:
			fullpath = os.path.join(root, file)
			
			if len(extnames) > 0:
				for extname in extnames:
					if fullpath.endswith(extname) or fullpath.endswith(extname.upper()):
						pathlist.append(fullpath)
			elif len(extnames) == 0:
				pathlist.append(fullpath)
	return pathlist
	
	
def desktop() -> str:
	if "Windows" in platform():  # 其他平台没用过
		key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
		path = winreg.QueryValueEx(key, "Desktop")[0]
	else:  # 未测试
		path = os.path.expanduser("~/Desktop")
	return path
	
	
def monthNow() -> str:
	year = str(time.localtime()[0])
	month = str(time.localtime()[1])
	if len(month) == 1:
		month = f"0{month}"
	string = os.path.join(year, month)
	return string
	
	
def makeDirs(path):
	if not os.path.exists(path):
		os.makedirs(path)
	
	
def getFileTime(path):
	time1 = os.path.getctime(path)  # 文件创建日期，返回时间戳
	time2 = os.path.getmtime(path)  # 文件最近修改时间
	time3 = os.path.getatime(path)  # 文件最近访问时间
	return time1, time2, time3


def removeFile(*paths):
	for path in paths:
		if os.path.isdir(path):
			try:
				shutil.rmtree(path)
				logging.info(f"已经删除：{path}")
			except IOError:
				logging.error(f"删除失败：{path}")
		# os.makedirs(path)
		
		if os.path.isfile(path):
			name = os.path.split(path)[1]
			try:
				os.remove(path)
				logging.info(f"已经删除：{name}")
			except IOError:
				logging.error(f"删除失败：{path}")
	
	
def openFile(path):
	if os.path.exists(path):
		webbrowser.open(path)
	
	
@openFileCheck
def openText(path) -> str:
	text = ""
	try:
		with open(path, "r", encoding="UTF8") as f:
			text = f.read()
	except UnicodeError:
		try:
			with open(path, "r", encoding="GB18030") as f:
				text = f.read()
		except UnicodeError:  # Big5 似乎有奇怪的bug，不过目前似乎遇不到
			try:
				with open(path, "r", encoding="BIG5") as f:
					text = f.read()
			except UnicodeError:
				with open(path, "r", encoding="Latin1") as f:
					text = f.read()
	finally:
		return text


@openFileCheck
def openDocx(path) -> str:
	text = ""
	try:
		docx = Document(path)
	except IOError as e:
		logging.error(e)
	else:
		for para in docx.paragraphs:
			# print(para.paragraph_format)
			# print(para.paragraph_format.first_line_indent.pt)
			if para.style.name == "Normal Indent":  # 正文缩进
				text += f"　　{para.text}\n"
			elif para.paragraph_format.first_line_indent and para.paragraph_format.first_line_indent.pt >= 15:
				text += f"　　{para.text}\n"
			else:
				text += f"{para.text}\n"
	return text


@openFileCheck
def openDoc(path) -> str:
	text = ""
	word = DispatchEx('Word.Application')  # 独立进程
	word.Visible = 0  # 0为后台运行
	word.DisplayAlerts = 0  # 不显示，不警告
	
	try:
		docx = word.Documents.Open(path)
	except IOError as e:
		logging.error(e)
	else:
		text = docx.Content.Text.replace("\r\r", "\n")
		if docx.Paragraphs.CharacterUnitFirstLineIndent == 2:  # 首行缩进转空格
			texts = ["", ] + text.split()
			text = "\n　　".join(texts).strip("\n")
		# print(len(text), text, sep="\n")
		docx.Close(True)
	finally:
		word.Quit()
		return text


@openFileCheck
def openJson(path) -> any:
	try:
		with open(path, "rb") as f:
			data = json.load(f)
	except IOError as e:
		logging.error(e)
	else:
		return data
	

@openFileCheck
def openExcel(path):  # 打开软件手动操作
	excel = DispatchEx('Excel.Application')  # 独立进程
	excel.Visible = 1  # 0为后台运行
	excel.DisplayAlerts = 0  # 不显示，不警告
	try:
		excel.Workbooks.Open(path)  # 打开文档
		print("打开Excel……")
	except IOError as e:
		logging.error(e)


@saveFileCheck
def saveFile(path):
	try:
		with open(path, "w", encoding="UTF8") as f:
			f.write("")
	except IOError:
		logging.error(f"保存失败：{path}")
	else:
		logging.debug(f"已保存为：{path}")


@saveFileCheck
def saveText(path, text):
	if not path.endswith(".txt"):
		path += ".txt"
	try:
		with open(path, "w", encoding="UTF8") as f:
			f.write(text)
	except IOError:
		logging.error(f"保存失败：{path}")
	else:
		logging.debug(f"已保存为：{path}")


def saveTxt(path, text):
	return saveText(path, text)


@saveFileCheck
def saveTextDesktop(name, text):
	path = os.path.join(desktop(), name)
	saveText(path, text)
	

@saveFileCheck
def saveCsv(path, text):
	if not path.endswith(".csv"):
		path += ".csv"
	try:
		with open(path, "w", encoding="UTF-8-sig") as f:
			f.write(text)
	except IOError:
		logging.error(f"保存失败：{path}")
	else:
		logging.info(f"已保存为：{path}")
		

@saveFileCheck
def saveJson(path, data):
	if not path.endswith(".json"):
		path = f"{path}.json"
	try:
		with open(path, 'w', encoding="UTF8") as f:
			json.dump(data, f, ensure_ascii=False, indent=4)
	except IOError:
		logging.error(f"保存失败：{path}")
	# else:
	# 	logging.info(f"已保存为：{path}")


@saveFileCheck
def saveDocx(path, text, *, original=""):
	if original:
		docx = Document(original)
		for para in docx.paragraphs:
			para.clear()
			para._element.getparent().remove(para._element)
	else:
		docx = Document(template_dotx)
	
	text = text.split("\n")
	for para in text:
		docx.add_paragraph(para)
		
	try:
		docx.save(path)
	except IOError as e:
		logging.error(e)
	# else:
	# 	logging.debug(f"已保存为：{path}")


@saveFileCheck
def saveDoc(path, text):
	extdict = {
		".docx": 16,
		# ".docm": "",  # 启用宏的文档
		".dotx": 1,  # Word 模板
		# ".dotm": "",  # 启用宏的模板
		".doc": 0,  # 97-03 .doc
		".pdf": 17,
		".xps": 18,
		".txt": 7,  # Unicode text
		".odt": 23, # OpenDocument Text format
	}
	
	word = DispatchEx('Word.Application')  # 独立进程
	word.Visible = 0  # 0为后台运行
	word.DisplayAlerts = 0  # 不显示，不警告
	try:
		docx = word.Documents.Add(template_dotm)  # 创建新的word文档
	except IOError as e:
		logging.error(e)
	else:
		s = word.Selection
		s.FormatText = text  # 写入文本
		docx.Application.Run("小说排版")  # 运行宏
		extname = os.path.splitext(path)[1]
		if extname == ".txt":
			docx.SaveAs2(path, 7, Encoding=65001, AddToRecentFiles=False, AllowSubstitutions=False,
			             LineEnding=0)  # txt UTF8 CRLF
		else:
			docx.SaveAs2(path, extdict.get(extname, 16))
		logging.info(f"已保存为：{path}")
		docx.Close(True)
	finally:
		word.Quit()


@timer
def zipFile(path, password="", delete=0, dir="") -> str:
	"""使用 pyzipper ，可用aes256加密，压缩传入的文件或文件夹
	Args:
		path: path 待压缩的文件/文件夹路径
		password: password 密码
		delete: 不为0时，压缩后删除源文件
		dir: 检测 dir 是否在 path 内，以修复 PixivSeries 的 TranslateAsZip 压入未翻译文件的bug
	"""
	
	def zipSingleFile(path, zippath, password):
		if password:
			encryption = zf.WZ_AES
		else:
			encryption = None
			
		with zf.AESZipFile(zippath, 'w', compression=zf.ZIP_LZMA, encryption=encryption) as z:
		# with zf.ZipFile(zippath, 'w', compression=zf.ZIP_DEFLATED) as z:
			z.setpassword(password.encode(encoding="utf-8"))
			name = os.path.split(path)[1]
			z.write(filename=path, arcname=name)  # 压缩的文件，zip内路径
	
	def zipFolder(path, zippath, password):
		files = findFile(path, )   # 获取目录下所有文件
		if password:
			encryption = zf.WZ_AES
		else:
			encryption = None
			
		with zf.AESZipFile(zippath, 'w', compression=zf.ZIP_LZMA, encryption=encryption) as z:
			# with zf.ZipFile(zippath, 'w', compression=zf.ZIP_DEFLATED) as z:
			z.setpassword(password.encode(encoding="utf-8"))
			
			for filepath in files:
				# print(filepath)
				if dir in filepath:
					arcname = filepath.replace(path, "")
					# print(filepath, arcname, sep="\n")
					z.write(filename=filepath, arcname=arcname)  # 压缩的文件，zip内路径
	
	if os.path.isdir(path):
		zipfilepath = f"{path}.zip"
		removeFile(zipfilepath)
		zipFolder(path, zipfilepath, password)
		
	elif os.path.isfile(path):
		zipfilepath = f"{os.path.splitext(path)[0]}.zip"
		removeFile(zipfilepath)
		zipSingleFile(path, zipfilepath, password)
		
	else:
		zipfilepath = ""
		print(f"不存在：{path}")
		os._exit(0)
		
	if delete != 0:
		removeFile(path)
	
	zipname = os.path.split(zipfilepath)[1]
	print(f"压缩完成：{zipname}")
	# print(zipfilepath)
	return zipfilepath


# @timethis
def unzipFile(path, password="", mode=0, delete=0) -> str:
	"""使用 pyzipper 可解压加密的zip文件（ase256 与 ZipCrypto）,前者会快得多
	智能解压：path传入zip路径解压zip，传入文件夹则解压其路径下的zip
	智能解压：zip内无文件夹，则会新建以zip文件名为名的文件夹，zip只有单文件不新建文件夹
	常规软件压缩设置：勾选zip使用Unicode文件名，避免解压后文件名乱码
	Args:
		path: path 待解压的zip文件/含有zip文件的文件夹路径
		password: password 密码
		mode: mode=1 解压zip内部的zip文件
		delete: delete=1 解压后删除zip源文件；同时 mode=1 解压后会删除所有zip
	"""
	
	if os.path.isdir(path):
		ziplist = findFile(path, ".zip")
		if len(ziplist) == 0:
			print(f"{path} 目录下无zip文件")
		for zipfile in ziplist:
			unzipFile(zipfile, password, mode=mode, delete=delete)
		
	elif zf.is_zipfile(path):
		name = os.path.split(path)[1]
		dir = os.path.splitext(path)[0]
		if os.path.exists(dir):
			removeFile(dir)
		
		with zf.AESZipFile(path, "r") as z:
		# with zf.ZipFile(path, "r") as z:
			comment = z.comment.decode(encoding="utf-8")
			if comment:
				print(f"压缩文件注释:{comment}")
			
			if z.namelist()[0].endswith("/"): 	# 内有文件夹，直接解压
				dir = os.path.split(path)[0]
				directory = os.path.join(dir, z.namelist()[0])
				removeFile(directory)
			elif len(z.namelist()) == 1:        # 单文件不新建文件夹
				dir = os.path.split(path)[0]
			else:                               # 多文件，新建文件夹
				dir = os.path.splitext(path)[0]
			
			try:
				logging.info(f"{name} 解压中……")
				# z.extractall(dir, members=z.namelist(), pwd=password.encode('utf-8'))
				for file in z.namelist():
					z.extract(file, dir, password.encode('utf-8'))
					if file.endswith(".zip") and mode:  # 解压zip内的zip
						path = os.path.join(dir, file)
						unzipFile(path, password, mode=mode, delete=delete)
						
				print(f"已解压：{name}")
			except RuntimeError:
				print(f"密码【{password}】错误，解压失败")
		
		if delete != 0:
			removeFile(path)  # 删除zip文件
		return dir
	
	
def test():
	print("测试")
	path = r"D:\Download\Github\FurryNovelsBot\Translated\龙龙.docx"
	openDocx(path)
	pass


if __name__ == '__main__':
	test()
	pass
