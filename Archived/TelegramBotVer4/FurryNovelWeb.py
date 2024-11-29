# !/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import json

import requests


def getId(string: [int, str]):
	if re.search(r"\d+", str(string)):
		return re.search(r"\d+", str(string)).group()


def getUrl(string: str) -> [str, list]:
	pattern = "(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"
	urls = re.findall(pattern, string)
	if len(urls) == 1:
		return urls[0]
	else:
		return urls


# 向 FurryNovel.com 提交 Pixiv 链接
def uploadToWebSite(url):
	upload_url = f"https://api.furrynovel.com/api/library/push?url={getUrl(url)}"
	headers = {'Authorization': 'Bearer 84e5659b5b5a4b5a8c5a5a5a5a5a5a5a'}
	response = requests.request("GET", upload_url, headers=headers)
	# print(f"{url} {response.text}")
	return response.text


# 从 FurryNovel.com 获取 Pixiv 链接
def getOriginalLink(url):
	upload_url = f"https://api.furrynovel.com/api/zh/novel/{getId(url)}"
	response = requests.request("GET", upload_url)
	data = json.loads(response.text)
	if data["code"] == 500:
		return None
	else:
		novel_id = data["data"]["source_id"]
		if "pixiv" in data["data"]["source"]:
			if data["data"]["ext_data"]["oneshot"]: # 单篇小说
				novel_url = f"https://www.pixiv.net/novel/show.php?id={novel_id}"
			else:
				novel_url = f"https://www.pixiv.net/novel/series/{novel_id}"
		else:
			novel_url = f"https://www.bilibili.com/read/readlist/rl{novel_id}"
		if __name__ == "__main__":
			print(f"{url} 转换为：{novel_url}")
	return novel_url


if __name__ == "__main__":
	# url = "https://www.pixiv.net/novel/show.php?id=21883603"
	# uploadToWebSite(url)
	url = "https://www.furrynovel.com/novel/491"
	getOriginalLink(url)
	pass
