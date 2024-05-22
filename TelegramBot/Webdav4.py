#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import time
import logging

from webdav4.client import Client, HTTPError
from httpx import ConnectError, ReadTimeout, WriteTimeout, RemoteProtocolError

from FileOperate import makeDirs, removeFile, zipFile, timer
from configuration import webdavs4 as webdavs, encryptlist, PASSWORD, testMode


# webdavs = {
# 	"jianguoyun": {
# 		"baseurl": "https://dav.jianguoyun.com/dav/",
# 		"username": "",  # 你的账号，支持多组
# 		"password": ""   # 你的密码
# 	},
# }


def monthNow():
	year = time.localtime()[0]
	month = time.localtime()[1]
	if len(f"{month}") == 1:
		month = f"0{month}"
	string = f"{year}/{month}"
	return string


def makedirs(client, path: str):
	directory = os.path.split(path)[0]
	if not client.exists(directory):
		pathlist = path.split("/")
		for i in range(1, len(pathlist)):  # 去文件名
			folder = "/".join(pathlist[:i])
			if not client.exists(folder):
				client.mkdir(folder)
			elif folder:
				continue
				

# @timer
def upload(webdav: dict, path: str, folder="", monthnow=0):
	url = webdav.get("baseurl").split("/")[2]
	name = os.path.split(path)[1]
	client = Client(
		webdav.get("baseurl"),
		auth=(webdav.get("username"), webdav.get("password")),
		proxies={}, timeout=10)
	
	if monthnow:
		pathlist = ["兽人小说", folder, f"{monthNow()}", name]
	else:
		pathlist = ["兽人小说", folder, name]
	webdavpath = "/".join(pathlist).replace("//", "/")
	# print(f"Webdav 文件上传路径：{webdavpath}")
	
	try:
		makedirs(client, webdavpath)
	except ConnectError:  # httpx.ConnectError
		print(f"无法连接到 {url}")
	except RemoteProtocolError:
		pass # 屏蔽错误信息 httpx.RemoteProtocolError
	except Exception as e:
		logging.exception(e)
	
	try:
		client.upload_file(path, webdavpath, True)
		print(f"【{name}】已上传至：{url}/{webdavpath}")
	except FileNotFoundError as e:
		print(f"目录不存在，{name}上传失败")
		logging.warning(e)
	except (HTTPError, ConnectError) as e:
		print(f"【{name}】上传 {url} 失败")
		logging.warning(e)
	except (WriteTimeout, ) as e: # YandexDisk的错误
		print(f"【{name}】上传 {url} 失败")
		logging.warning(e)
	except ReadTimeout as e:    # 屏蔽 YandexDisk Timeout
		print(f"【{name}】已上传至：{url}")
		logging.info(e)
	except RemoteProtocolError:
		pass  # 屏蔽错误信息 httpx.RemoteProtocolError
	except Exception as e:
		logging.exception(e)


def uploadFile(path: str, folder: str = ""):
	for webdav in webdavs:
		webdav = webdavs.get(webdav)
		upload(webdav, path, folder)
	
	
def uploadNovel(path: str, folder: str, *, encrypt=0, delete=0):
	# 默认使用 encryptlist 进行加密；encrypt=1 强制加密
	# delete=1 时，上传后删除源文件
	
	zippath = f"{os.path.splitext(path)[0]}.zip"  # 压缩后路径
	for webdav in webdavs.keys():
		webdav = webdavs.get(webdav)
		baseurl = webdav.get("baseurl")
		if encrypt == 1 or baseurl in encryptlist:  # 加密压缩
			if not os.path.exists(zippath):
				filepath = zipFile(path, password=PASSWORD)
			else:
				filepath = zippath
		else:  # 直接上传
			filepath = path
		upload(webdav, filepath, folder, monthnow=1)  # 按时间分类
		# break
		
	if os.path.exists(zippath):
		removeFile(zippath)
	if delete != 0:
		removeFile(path)  # 删除源文件


def remove(webdav: dict, path: str):
	# path="2022/05"时，只删除05文件夹及其子文件（夹）
	url = webdav.get("baseurl").split("/")[2]
	client = Client(
		webdav.get("baseurl"),
		auth=(webdav.get("username"), webdav.get("password")),
		proxies={}, timeout=10)
	
	if client.exists(path):
		try:
			client.remove(path)
			print(f"【{path}】在 {url} 已经删除")
		except HTTPError as e:
			print(f"【{path}】在 {url} 删除失败：{e}")
			# logging.warning(e)
		except Exception as e:
			logging.exception(e)
	else:
		logging.info(f"{path} 不存在 {url}")
	
	
def removeAll(path: str):
	for webdav in webdavs:
		webdav = webdavs.get(webdav)
		remove(webdav, path)
		

# def find(path):
# 	files = []
# 	webdav = webdavs["YandexDisk"]
# 	client = Client(
# 		webdav.get("baseurl"),
# 		auth=(webdav.get("username"), webdav.get("password")),
# 		proxies={}, timeout=10)
# 	files.extend(client.ls(path, detail=False))
# 	return files


@timer
def findFiles(folder="小说", year=0):
	files = []
	if not year:
		year = time.localtime()[0]
		
	webdav = webdavs["YandexDisk"]
	client = Client(
		webdav.get("baseurl"),
		auth=(webdav.get("username"), webdav.get("password")),
		proxies={}, timeout=10)
	
	for month in range(0, 12):
		month += 1
		if len(f"{month}") == 1:
			month = f"0{month}"
		path = f"兽人小说/{folder}/2023/{month}"
		files.extend(client.ls(path, detail=False))
	return files
	
	
def download(from_path, to_folder):
	webdav = webdavs["YandexDisk"]
	client = Client(
		webdav.get("baseurl"),
		auth=(webdav.get("username"), webdav.get("password")),
		proxies={}, timeout=10)
	
	print(from_path)
	to_path = os.path.join(to_folder, from_path.replace("兽人小说/小说", ""))
	makeDirs(os.path.dirname(to_path))
	print(to_path)
	client.download_file(from_path, to_path)
	
	
@timer
def downloadFiles(to_folder, year=time.localtime()[0]):
	webdav = webdavs["YandexDisk"]
	client = Client(
		webdav.get("baseurl"),
		auth=(webdav.get("username"), webdav.get("password")),
		proxies={}, timeout=10)
	
	# to_folder = r"D:\Download\Browser"
	if os.path.exists(os.path.join(to_folder, f"{year}")):
		removeFile(os.path.join(to_folder, f"{year}"))
	
	files = findFiles("小说", year)
	for i in range(len(files)):
		file = files[i]
		to_path = os.path.join(to_folder, os.path.relpath(file, "兽人小说"))
		makeDirs(os.path.dirname(to_path))
		# print(file, to_path, sep="\n")
		client.download_file(file, to_path)
		name = os.path.basename(file)
		rate = round(100 * i / len(files), 2)
		print(f"正在下载【{name}】，当前进度{rate}%")
	
	
def addWebdavDict():
	d0 = {}
	i = 1
	text = " "  # 外层 while 第一次运行
	webdavurl = ""
	username = ""
	password = ""
	while text:
		
		# 获取网址链接
		while text:
			text = input(f"\n请输入第{i}组 Webdav 服务网址，按 Enter 键确认：\n")
			pat = "(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"
			if re.findall(pat, text) and "dav" in text:
				webdavurl = re.findall(pat, text)[0]
				webdavname = webdavurl.split(".")[1]
				if webdavname not in d0:
					print(f"第{i}组 Webdav 服务网址：{webdavurl}")
					break
				else:
					print(f"{webdavname}已存在，请录入其他数据或按 Enter 键退出")
					text = input(f"\n请输入第{i}组 Webdav 服务网址：\n")
			else:
				print("输入有误，请重新输入，退出请按 Enter 键\n")
		
		# 获取邮箱地址
		while text:
			text = input(f"\n请输入第{i}组 Webdav 账户，按 Enter 键确认：\n")
			pat = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
			if re.findall(pat, text):
				username = re.findall(pat, text)[0]
				print(f"第{i}组 Webdav 账号：{username}")
				break
			else:
				print("输入有误，请重新输入，退出请按 Enter 键")
		
		# 获取密码
		while text:
			text = input(f"\n请输入第{i}组 Webdav 密码，按 Enter 键确认：\n")
			if text:
				password = text
				print(f"第{i}组 Webdav 密码：{password}")
				break
			else:
				print("输入有误，请重新输入，退出请按 Enter 键")
		
		webdavname = webdavurl.split(".")[1]
		if webdavurl and username and password:
			d0.update({webdavname: {"baseurl": webdavurl, "username": username, "password": password}})
			i += 1
	
	print("已录入数据如下：\n请将输出结果写入配置文件中")
	print("webdavs = {")
	for key in d0:
		print(f"{d0[key]},")
	print("}")
	# print(d0)
	

def test():
	print("测试")


if __name__ == '__main__':
	testMode = 1
	if testMode:
		test()
	else:
		addWebdavDict()
