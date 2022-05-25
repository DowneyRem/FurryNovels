#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import logging

from webdav4.client import Client, HTTPError
from httpx import ConnectError

from FileOperate import removeFile, timethis
from config import webdavdict4 as webdavdict


# webdavdict = {
# 	"jianguoyun": {
# 		"baseurl": "https://dav.jianguoyun.com/dav/",
# 		"username": "",  # 你的账号，支持多组
# 		"password": ""   # 你的密码
# 	},
# }

		
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
	
	url = baseurl.split("/")[2]
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
		print("【{}】已上传至：{}".format(name, url))
	except FileNotFoundError as e:
		print("目录不存在，上传失败：{}".format(name))
		logging.warning(e)
	except (HTTPError, ConnectError) as e:
		print("【{}】上传 {} 失败".format(name, url))
		logging.warning(e)
	except Exception as e:
		logging.exception(e)
	
	
# @timethis
def uploadAll(path, delete=0):
	# delete 不为0时，上传后删除源文件
	webdavs = list(webdavdict.keys())
	# print(webdavs)
	for webdav in webdavs:
		webdav = webdavdict.get(webdav)
		# print(webdav)
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
