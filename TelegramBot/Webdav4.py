#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import logging

from webdav4.client import Client, HTTPError
from httpx import ConnectError, ReadTimeout, WriteTimeout

from FileOperate import removeFile, zipFile, timethis
from config import webdavdict4 as webdavdict, encryptlist


# webdavdict = {
# 	"jianguoyun": {
# 		"baseurl": "https://dav.jianguoyun.com/dav/",
# 		"username": "",  # 你的账号，支持多组
# 		"password": ""   # 你的密码
# 	},
# }


logging.basicConfig(format='[line:%(lineno)d]-%(levelname)s: %(message)s', level=logging.INFO)


def monthNow():
	year = str(time.localtime()[0])
	month = str(time.localtime()[1])
	if len(month) == 1:
		month = "0" + month
	string = "{}/{}".format(year, month)
	return string


# @timethis
def upload(webdav:dict, path):
	def makedirs(path):
		a = path.split("/")
		for i in range(1, len(a)):  # 去文件名
			b = "/".join(a[:i])
			if not client.exists(b):
				client.mkdir(b)
			elif b:
				continue
				
	baseurl  = webdav.get("baseurl")
	username = webdav.get("username")
	password = webdav.get("password")
	client = Client(baseurl, auth=(username, password) ,proxies={}, timeout=10)
	
	url = baseurl.split("/")[2]
	name = os.path.split(path)[1]
	if "jianguoyun" in baseurl:  # 坚果云根目录无法分享
		webdavPath = "/兽人小说/兽人小说/{}/{}".format(monthNow(), name)
	else:
		webdavPath = "/兽人小说/{}/{}".format(monthNow(), name)
	# print(webdavPath)
	
	dir = os.path.split(webdavPath)[0]
	try:
		if not client.exists(dir):
			makedirs(webdavPath)
	except :   #httpx.ConnectError
		print(f"无法连接到 {url}")
	
	try:
		client.upload_file(path, webdavPath, True)
		print("【{}】已上传至：{}".format(name, url))
	except FileNotFoundError as e:
		print("目录不存在，{}上传失败".format(name))
		logging.warning(e)
	except (HTTPError, ConnectError) as e:
		print("【{}】上传 {} 失败".format(name, url))
		logging.warning(e)
	except (WriteTimeout) as e: # YandexDisk的错误
		print("【{}】上传 {} 失败".format(name, url))
		logging.warning(e)
	except ReadTimeout as e:    # 屏蔽YandexDisk的Timeout
		print("【{}】已上传至：{}".format(name, url))
		logging.info(e)
	except Exception as e:
		logging.exception(e)
	
	
def uploadAll(path, *, encrypt=0, delete=0):
	# 默认使用 encryptlist 进行加密；encrypt=1 强制加密
	# delete 不为0时，上传后删除源文件
	
	zippath = "{}.zip".format(os.path.splitext(path)[0])  #压缩后路径
	webdavs = list(webdavdict.keys())
	for webdav in webdavs:
		webdav = webdavdict.get(webdav)
		baseurl = webdav.get("baseurl")
		if encrypt == 1 or baseurl in encryptlist:
			if not os.path.exists(zippath):
				filepath = zipFile(path, "furry")  # 加密压缩
			else:
				filepath = zippath
		else:
			filepath = path
		upload(webdav, filepath)
		
	if os.path.exists(zippath):
		removeFile(zippath)
	if delete != 0:
		removeFile(path)  # 删除源文件


def remove(webdav: dict, path):
	# path="2022/05"时，只删除05文件夹及其子文件（夹）
	
	baseurl = webdav.get("baseurl")
	username = webdav.get("username")
	password = webdav.get("password")
	client = Client(baseurl, auth=(username, password), proxies={})
	url = baseurl.split("/")[2]
	
	if client.exists(path):
		try:
			client.remove(path)
			print("【{}】在 {} 已经删除".format(path, url))
		except HTTPError as e:
			print("【{}】在 {} 删除失败：{}".format(path, url, e))
			# logging.warning(e)
		except Exception as e:
			logging.exception(e)
	else:
		logging.info("{} 不存在 {}".format(path, url))
	
	
def removeAll(path):
	webdavs = list(webdavdict.keys())
	for webdav in webdavs:
		webdav = webdavdict.get(webdav)
		remove(webdav, path)

def main():
	pass

if __name__ == '__main__':
	pass
