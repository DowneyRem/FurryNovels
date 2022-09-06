#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
from functools import wraps


def checkNone(fun):
	@wraps(fun)
	def wrapper(*args, **kwargs):
		try:
			r = fun(*args, **kwargs)
		except Exception as e:
			print(e)
			r = ""
		return r
	return wrapper
	
	
@checkNone
def formatFileName(text: str) -> str:
	text = re.sub('[/\:*?"<>|]', ' ', text)
	text = text.replace('  ', '')
	return text


@checkNone
def formatNovelName(name: str) -> str:
	if re.findall("[(（].*(委托|赠给).*[)）]", name):  # 梦川云岚OwO，优化
		# 赏金猎人2——（果果委托)；克隆实验——（赠给艾兰）
		pattern = "(.*)((?:—|-|_){2,} ?.*)"
		if re.findall(pattern, name):
			text = re.findall(pattern, name)
			# print(text)
			name = text[0][0].strip()

	elif re.findall("([给給]?.+?的?(?:委托|赠文|无偿))", name):
		# pattern = "((?:给|給)?.+?的?(?:委托|赠文|无偿))(?::|：|;|；|,|，)?(.+?)((?:（| ).*）?)"
		# pattern = "((?:给|給)?.+?的?(?:委托|赠文|无偿))(?::|：|;|；|,|，)?(.+)"
		pattern = "((?:给|給)?.+?的?(?:委托|赠文|无偿|合委))[:;, ：；，]?(.+)"
		# todo：XXX 委托 标记符 名称，只考虑从后半部分提取名称
		text = re.findall(pattern, name)
		if text:
			# print(text)
			# a = text[0][0].strip()  # a unused
			b = text[0][1].strip()
			b = re.sub("[(（]?[0-9]+([)）])?", "", b)
			b = b.replace("摸鱼", "")

			if len(b) >= 1:
				name = text[0][1].strip()

	name = name.replace("《", "").replace("》", "")
	name = formatFileName(name)
	# print(name)
	return name


@checkNone
def formatCaption(caption: str) -> str:
	caption = caption.replace("<br />", "\n").replace("<br>", "\n")
	caption = caption.replace("<strong>", "").replace("</strong>", "")
	caption = caption.replace("&amp;", "&")
	caption = caption.replace("\n\n", "\n")
	
	
	# pattern = r'<a href="pixiv://(illusts|novels|users)/[0-9]{5,}">(illust|novel|user)/[0-9]{5,}</a>'
	# 不清楚为什么用完整的表达式反而会匹配不了，不得已拆成了3份
	if "illust" in caption:
		# <a href="pixiv://illusts/12345">illust/12345</a>
		pattern = '<a href="pixiv://illusts/[0-9]{5,}">illust/[0-9]{5,}</a>'
		a = re.findall(pattern, caption)
		for i in range(len(a)):
			string = a[i]
			# print(string)
			id = re.search("[0-9]{5,}", string).group()
			link = " https://www.pixiv.net/artworks/{} ".format(id)
			caption = caption.replace(string, link)
	
	if "novel" in caption:
		# <a href="pixiv://novels/12345">novel/12345</a>
		pattern = '<a href="pixiv://novels/[0-9]{5,}">novel/[0-9]{5,}</a>'
		a = re.findall(pattern, caption)
		for i in range(len(a)):
			string = a[i]
			id = re.search("[0-9]{5,}", string).group()
			link = " https://www.pixiv.net/novel/show.php?id={} ".format(id)
			caption = caption.replace(string, link)
	
	if "user" in caption:
		# <a href="pixiv://users/12345">user/12345</a>
		pattern = '<a href="pixiv://users/[0-9]{5,}">user/[0-9]{5,}</a>'
		a = re.findall(pattern, caption)
		for i in range(len(a)):
			string = a[i]
			id = re.search("[0-9]{5,}", string).group()
			link = " https://www.pixiv.net/users/{} ".format(id)
			caption = caption.replace(string, link)
	
	if "target" in caption:
		# 一般a标签
		# <a href="https://deadmanshand.fanbox.cc/" target="_blank">https://deadmanshand.fanbox.cc/</a>
		pattern = '''<a href="(https://.*)" target=(?:'|")_blank(?:'|").*>https://.*</a>'''
		a = re.findall(pattern, caption)
		for i in range(len(a)):
			link = " {}".format(a[i])
			caption = re.sub(pattern, link, caption, 1)
	return caption


@checkNone
def formatPixivText(text: str) -> str:
	# 处理 Pixiv 标识符
	
	# [newpage]  [chapter: 本章标题]
	# text = self.formatNovelText(self.text)
	text = text.replace("[newpage]", "\n\n")
	a = re.findall("\\[chapter:(.*)]", text)
	for i in range(len(a)):
		string = a[i]
		if "第" in string and "章" in string:
			string = string.replace("章", "节")
		elif re.search("\\d+", string):
			string = "第{}节".format(string)
		elif re.search("[二三四五六七八九]?十?[一二三四五六七八九十]", string):
			string = "第{}节".format(string)
		else:
			string = "第{}节 {}".format(i + 1, string)
		text = re.sub("\\[chapter:(.*)]", string, text, 1)

	# [jump: 链接目标的页面编号]
	if "[jump:" in text:
		a = re.findall("\\[jump:(.*)]", text)
		for i in range(len(a)):
			string = a[i]
			string = "跳转至第{}节".format(string)
			text = re.sub("\\[jump:(.*)]", string, text, 1)
	
	# [pixivimage: 作品ID]
	if "[pixivimage:" in text:
		a = re.findall("\\[pixivimage: (.*)]", text)
		for i in range(len(a)):
			string = a[i].strip(" ")
			string = "插图：https://www.pixiv.net/artworks/{}".format(string)
			text = re.sub("\\[pixivimage:(.*)]", string, text, 1)
	
	# [uploadedimage: 上传图片自动生成的ID] 会被 pixivpy 转换
	if "[jumpuri:If" in text:
		pattern = "\\[\\[jumpuri:If you would like to view illustrations, please use your desktop browser.>https://www.pixiv.net/n/[0-9]{5,}]] "
		string = "【本文内有插图，请在Pixiv查看】"
		text = re.sub(pattern, string, text)
	
	# [[jumpuri: 标题 > 链接目标的URL]]
	if "[jumpuri:" in text:
		a = re.findall("\\[{2}jumpuri: *(.*) *> *(.*)]{2}", text)
		for i in range(len(a)):
			name = a[i][0]
			link = a[i][1]
			if link in name:
				text = re.sub("\\[{2}jumpuri: *(.*) *> *(.*)]{2}", link, text, 1)
			else:
				string = "{}【{}】".format(name, link)
				text = re.sub("\\[{2}jumpuri: *(.*) *> *(.*)]{2}", string, text, 1)
	
	return text


@checkNone
def formatTextSpace(text: str) -> str:
	space = """​
		零宽不连字    通用标点 ‌
		零宽连        通用标点 ‍
		窄式不换行空格 通用标点  
		中数学空格     通用标点	 
		文字连接符    通用标点	⁠
		零宽不换行空格（Zero Width No-Break Space） ﻿
		"""
	# pattern = " ​  "
	pattern = " ​     "
	text = re.sub(pattern, '', text)
	return text
	
	
@checkNone
def formatTextPunctuation(text: str) -> str:
	text = re.sub("\\.{3,}", "……", text)  # 省略号标准化
	text = re.sub("。。。{3,}", "……", text)
	text = re.sub("!{3,}", "!{3}", text)  # 感叹号标准化
	text = re.sub("！{3,}", "！{3}", text)
	# text = text.replace("&quot;", ",")  # 避免转码，已使用纯文本翻译
	# text = text.replace("&#39;", "'")
	return text


@checkNone
def formatTextIndent(text: str) -> str:
	text = re.sub("\n{3,}", "\n\n", text) # 删除多余空行
	text = re.sub("\n +", "\n", text)     # 删除半角空格
	text = re.sub("\n　+", "\n", text)    # 删除全角空格
	text = text.replace("\n", "\n　　")   # 添加全角空格
	return text


@checkNone
def formatText(text: str) -> str:
	text = formatTextSpace(text)
	text = formatTextPunctuation(text)
	text = formatTextIndent(text)
	text = formatPixivText(text)
	return text
	
	
if __name__ == '__main__':
	pass
