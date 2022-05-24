#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os, shutil
import time
from webdav3.client import Client

# from FileOperate import removeFile, timethis
# from config import webdavdict3 as webdavdict


webdavdict = {
	"jianguoyun": {
		"baseurl": "https://dav.jianguoyun.com/dav/",
		"username": "",  # 你的账号，支持多组
		"password": ""   # 你的密码
	},
}


def timethis(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		start = time.perf_counter()
		r = func(*args, **kwargs)
		end = time.perf_counter()
		print('{}.{} : {}'.format(func.__module__, func.__name__, end - start))
		return r
	return wrapper


def removeFile(path):
	if os.path.isdir(path):
		shutil.rmtree(path)
	os.makedirs(path)
	if os.path.isfile(path):
		os.remove(path)
		
		
def monthNow():
	year = str(time.localtime()[0])
	month = str(time.localtime()[1])
	if len(month) == 1:
		month = "0" + month
	string = "{}/{}".format(year, month)
	return string


@timethis
def upload(options, path):
	client = Client(options)
	name = os.path.split(path)[1]
	webdavPath = "兽人小说/{}/{}".format(monthNow(), name)
	# print(webdavPath)
	try:
		client.upload(webdavPath, path)
		url = options.get("webdav_hostname")
		url = url.split("/")[2]
		print("{} 已上传至：{}".format(name, url))
	except :
		print("请检查网络或代理")
	

# @timethis
def uploadAll(path, delete=0):
	# delete 不为0时，上传后删除源文件
	webdavs =list(webdavdict.items())
	print(list(webdavdict.keys()))
	for webdav in webdavs:
		# print(webdav[0])
		options = webdav[1]
		upload(options, path)
		
	if delete != 0:
		name = os.path.split(path)[1]
		try:
			removeFile(path)  # 删除源文件
			print("【{}】已经删除".format(name))
		except IOError:
			print("【{}】删除失败".format(name))
		
		
if __name__ == '__main__':
	pass
