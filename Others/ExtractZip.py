#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os, shutil
import time
import logging
# import pyzipper as zf
from functools import wraps
from platform import platform


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
	# 省略 extnames 参数可以获取全部文件
	for dir in os.listdir(path):
		dir = os.path.join(path, dir)
		if os.path.isdir(dir):
			findFile(dir, *extnames)
		
		if os.path.isfile(dir):
			if len(extnames) > 0:
				for extname in extnames:
					(name, ext) = os.path.splitext(dir)
					if ext==extname:
						pathlist.append(dir)
			elif len(extnames)==0:
				pathlist.append(dir)
	return pathlist


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
			
			
def zipFile(path, password="", delete=0):
	# 使用 pyzipper ，可用aes256加密，压缩传入的文件或文件夹
	# parm delete 不为0时，压缩后删除源文件
	
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
		list = findFile(path, )  # 获取目录下所有文件
		if password:
			encryption = zf.WZ_AES
		else:
			encryption = None
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
	
	if delete!=0:
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
		if len(ziplist)==0:
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
			if z.namelist()[0].endswith("/"):  # 内有文件夹，直接解压
				dir = os.path.split(path)[0]
				directory = os.path.join(dir, z.namelist()[0])
				removeFile(directory)
			elif len(z.namelist())==1:  # 单文件不新建文件夹
				dir = os.path.split(path)[0]
			else:  # 多文件，新建文件夹
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
		
		if delete!=0:
			removeFile(path)  # 删除zip文件
		return dir


@timethis
def extract(*, delete=0):
	try:
		import pyzipper as zf
		global zf
	except ModuleNotFoundError:
		print("请安装 pyzipper 模块")
		logging.warning("请安装 pyzipper 模块")
		
	else:
		path = os.getcwd()
		ziplist = findFile(path, ".zip")
		if ziplist:
			for zip in ziplist:
				unzipFile(zip, password="furry", mode=1, delete=1)
				print("————"*15)
			if "Windows" not in platform():
				time.sleep(5)
		else:
			print("请把【zip文件】与【本文件】放在同一文件夹下")
			print("放好后重新运行本脚本即可")
			time.sleep(10)
			
			
if __name__ == '__main__':
	import sys
	print(sys.version)
	extract(delete=1)

