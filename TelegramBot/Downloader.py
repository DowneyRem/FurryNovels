#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time

from LinpxClass import LinpxFactory, LinpxSeries
from FileOperate import readFile, saveFile, findFile, copyFile, openFile, unzipFile
from FurryNovelWeb import getUrl

from configuration import novel_folder, down_folder, USE_Pixiv
if USE_Pixiv:
	from PixivClass import PixivFactory, PixivSeries


def saveLinksToFile():
	path = r""
	folder = unzipFile(path)
	files = findFile(folder, ".txt")
	# print(files)
	links = []
	for file in files:
		links.append(getUrl(readFile(file)))
	for link in links:
		print(link)
	text = "\n".join(links)
	path = os.path.join(os.path.dirname(path), "links.txt")
	print(path)
	saveFile(path, text)


def getPixivLinks(path) -> list:  # 读取 links.txt 文件；每行都是一个 Pixiv 链接
	links = readFile(path).split("\n")
	links_set = set(links)
	links_set.discard("")
	links = sorted(links_set, key=links.index)  # 去重，按原顺序排序

	if not links:
		raise AttributeError(f"{os.path.basename(path)}内无连接")
	return links


def download(path):  # 下载小说，保存错误信息
	folder = os.path.dirname(path)
	links = getPixivLinks(path)
	links2 = links.copy()
	error_links = []
	for link in links:
		try:
			if USE_Pixiv:
				pixiv_obj = PixivFactory(link)
				if pixiv_obj.obj.series_id:
					pixiv_obj = PixivFactory(pixiv_obj.obj.series_url)
				if isinstance(pixiv_obj.obj, PixivSeries):
					pixiv_obj.obj.commission = False  # 默认视为长篇小说，下载为 txt 合集
					
			else:
				pixiv_obj = LinpxFactory(link)
				if pixiv_obj.obj.series_id:
					pixiv_obj = LinpxFactory(pixiv_obj.obj.series_url)
				if isinstance(pixiv_obj.obj, LinpxSeries):
					pixiv_obj.obj.commission = False  # 默认视为长篇小说，下载为 txt 合集
					
			pixiv_obj.save()
			links2.remove(link)
		except Exception as e:
			error_links.append({link: e.__str__()})
			print(f"{e}\n{link} 可能未能完成下载")
	
	if True:
		file = os.path.join(folder, "links.txt")
		saveFile(file, "\n".join(links2))
		file = os.path.join(folder, "links.failure.json")
		saveFile(file, error_links)
	
	
def downloader(path=""):  # 循环下载未完成下载的小说
	if not path:  # 检测 links.txt 是否存在
		path = os.path.join(down_folder, "links.txt")
	if not os.path.exists(path):
		saveFile(path, "")
		print(f"请在以下文件中存放需要下载的小说链接：\n{path}")
		time.sleep(5)
	
	else: # 循环下载未完成下载的小说
		copyFile(path, os.path.join(os.path.dirname(path), "links.backup.txt"))
		try:
			for i in range(DownloadTimes):
				print(f"\n第{i + 1}次下载：")
				download(path)
				time.sleep(RetryInterval * 60)
		except AttributeError as e:
			print(f"请在以下文件中存放需要下载的小说链接：\n{path}")
			time.sleep(5)
		else:
			openFile(novel_folder)
			

if __name__ == "__main__":
	DownloadTimes = 3  # 下载重试次数
	RetryInterval = 0  # 下载重试间隔时间(分)
	path = r""
	downloader(path)
