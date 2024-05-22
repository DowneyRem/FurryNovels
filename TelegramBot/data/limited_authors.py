#!/usr/bin/python
# -*- coding: UTF-8 -*-
from FileOperate import readFile, saveFile


def getData(path):
	data = []
	json = readFile(path)
	for item in json:
		for key in item:
			author = item["name"]
			author_id = item["id"]
			date = item["date"]
			if author_id:
				text = f"| {author} | https://www.pixiv.net/users/{author_id} | {date} |"
			else:
				text = f"| {author} | {author_id} | {date} |"
		print(text)
		data.append(text)
	return data
	
	
def saveData(data):
	path = f"./{name}.md"
	head = [
		"## 限制作者名单", "", ""
		"| 作者名 | 作者链接 | 申请时间 |",
		"| ----- | ------- | ------ |",
	]
	head.extend(data)
	text = "\n".join(head)
	saveFile(path, text)
	
	
if __name__ == '__main__':
	import os
	name = os.path.basename(os.path.splitext(__file__)[0])
	# path = "./limited_authors.json"
	path = f"./{name}.json"
	saveData(getData(path))
