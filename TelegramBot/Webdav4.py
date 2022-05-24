#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os, shutil
import time
from webdav4.client import Client

# from FileOperate import removeFile, timethis
# from config import webdavdict4 as webdavdict


webdavdict = {
	"jianguoyun": {
		'webdav_hostname': "https://dav.jianguoyun.com/dav/",
		'webdav_login': "",     # 你的账号，支持多组
		'webdav_password': "",  # 你的密码
		'disable_check': True,  # 有的网盘不支持check功能
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


def list2str(list):
	list = str(list)
	list = list.replace("[", "")
	list = list.replace("]", "")
	list = list.replace("'", "")
	list = list.replace(", ", "/")
	return list


@timethis
def upload(webdav:dict, path):
	def makedirs(path):
		if not client.exists(path):
			a = path.split("/")
			# print(a)
			for i in range(1, len(a)):  # 去文件名
				b = str(a[:i])
				b = list2str(b)
				if b:
					client.mkdir(b)
	
	baseurl  = webdav.get("baseurl")
	username = webdav.get("username")
	password = webdav.get("password")
	client = Client(baseurl, auth=(username, password), proxies={})
	
	name = os.path.split(path)[1]
	webdavPath = "兽人小说/{}/{}".format(monthNow(), name)
	# print(webdavPath)
	dir = os.path.split(webdavPath)[0]
	try:
		if not client.exists(dir):
			makedirs(webdavPath)
	except:   #httpx.ConnectError
		print("网络问题，检查代理等")
	
	try:
		client.upload_file(path, webdavPath,True)
		url = baseurl.split("/")[2]
		print("{} 已上传至：{}".format(name, url))
	except FileNotFoundError:
		print("目录不存在，上传失败：{}".format(name))
	except:  #httpx.ConnectError
		print("网络问题，检查代理等")
	
	
# @timethis
def uploadAll(path, delete=0):
	# delete 不为0时，上传后删除源文件
	webdavs = list(webdavdict.keys())
	print(webdavs)
	for webdav in webdavs:
		webdav = webdavdict.get(webdav)
		upload(webdav, path)
		
	if delete != 0:
		name = os.path.split(path)[1]
		try:
			removeFile(path)  # 删除源文件
			print("【{}】已经删除".format(name))
		except IOError:
			print("【{}】删除失败".format(name))


if __name__ == '__main__':
	pass
