#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import logging

from webdav3.client import Client
from webdav3.exceptions import *

from FileOperate import removeFile, timethis
from config import webdavdict3 as webdavdict


# webdavdict = {
# 	"jianguoyun": {
# 		'webdav_hostname': "https://dav.jianguoyun.com/dav/",
# 		'webdav_login': "",     # 你的账号，支持多组
# 		'webdav_password': "",  # 你的密码
# 		'disable_check': True,  # 有的网盘不支持check功能
# 	},
# }


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
	
	url = options.get("webdav_hostname").split("/")[2]
	name = os.path.split(path)[1]
	webdavPath = "兽人小说/{}/{}".format(monthNow(), name)
	# print(webdavPath)
	
	try:
		client.upload(webdavPath, path)
		print("【{}】已上传至：{}".format(name, url))
	except (ResponseErrorCode, NoConnection) as e:
		print("【{}】上传 {} 失败".format(name, url))
		logging.warning(e)
	except Exception as e:
		logging.exception(e)
		
		
# @timethis
def uploadAll(path, delete=0):
	# delete 不为0时，上传后删除源文件
	webdavs = list(webdavdict.items())
	# print(list(webdavdict.keys()))
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
