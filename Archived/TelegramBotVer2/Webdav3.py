#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import logging

from webdav3.client import Client
from webdav3.exceptions import *

from FileOperate import removeFile, zipFile, timethis
from config import webdavdict3 as webdavdict, encryptlist


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
	if "jianguoyun" in url:  # 坚果云根目录无法分享
		webdavPath = "/兽人小说/兽人小说/{}/{}".format(monthNow(), name)
	else:
		webdavPath = "兽人小说/{}/{}".format(monthNow(), name)
	# print(webdavPath)
	
	try:
		client.upload(webdavPath, path)
		print("【{}】已上传至：{}".format(name, url))
	except (ResponseErrorCode, NoConnection) as e:
		print("【{}】上传 {} 失败：".format(name, url))
		logging.warning(e)
	except Exception as e:
		logging.exception(e)
		
		
# @timethis
def uploadAll(path, *, encrypt=0, delete=0):
	# delete 不为0时，上传后删除源文件
	
	zippath = "{}.zip".format(os.path.splitext(path)[0])  #压缩后路径
	webdavs = list(webdavdict.items())
	for webdav in webdavs:
		options = webdav[1]
		url = options.get("webdav_hostname")
		if encrypt == 1 or url in encryptlist :
			if not os.path.exists(zippath):
				filepath = zipFile(path, "furry")
			else:
				filepath = zippath
		else:
			filepath = path
		upload(options, filepath)
		
	if os.path.exists(zippath):
		removeFile(zippath)
	if delete != 0:
		removeFile(path)  # 删除源文件
		
			
def remove(options, path):
	client = Client(options)
	url = options.get("webdav_hostname").split("/")[2]

	if client.check(path):
		try:
			client.clean(path)
			print("【{}】在 {} 已经删除".format(path, url))
		except (ResponseErrorCode, NoConnection) as e:
			print("【{}】在 {} 删除失败".format(path, url))
			logging.warning(e)
		except Exception as e:
			logging.exception(e)
	else:
		logging.info("{} 不存在 {}".format(path, url))
		
		
def removeAll(path):
	webdavs = list(webdavdict.items())
	for webdav in webdavs:
		options = webdav[1]
		remove(options, path)
		
		
if __name__ == '__main__':
	pass
