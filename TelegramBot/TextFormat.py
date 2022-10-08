#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
from html import unescape
from functools import wraps

from FileOperate import formatFileName
from config import cjklist, eulist, testMode


def checkNone(function):
	@wraps(function)
	def wrapper(*args, **kwargs):
		try:
			result = function(*args, **kwargs)
		except Exception as e:
			print(e)
			result = ""
		return result
	return wrapper
	
	
def isAlpha(string: str) -> bool:
	for char in string:
		if not "\u0000" <= char <= "\u007f":
			return False
	return True


def isContainAlpha(string: str) -> bool:
	for char in string:
		if "\u4e00" <= char <= "\u9fa5":
			return True
	return False


def isChinese(string: str) -> bool:  # 检验是否全是中文字符
	for char in string:
		if not "\u4e00" <= char <= "\u9fa5":
			return False
	return True


def isContainsChinese(string: str) -> bool: # 检验是否含有中文字符
	for char in string:
		if "\u4e00" <= char <= "\u9fa5":
			return True
	return False
	
	
@checkNone
def formatNovelName(name: str) -> str:
	if re.findall("[(（].*(委托|赠给).*[)）]", name):  # 梦川云岚OwO，优化
		# 赏金猎人2——（果果委托)；克隆实验——（赠给艾兰）
		pattern = "(.*)((?:—|-|_){2,} ?.*)"
		if re.findall(pattern, name):
			text = re.findall(pattern, name)
			# print(text)
			name = text[0][0].strip()
	
	elif re.findall("([给給]?.+?的?(?:委托|合委|赠文|无偿))", name):
		# pattern = "((?:给|給)?.+?的?(?:委托|赠文|无偿))(?::|：|;|；|,|，)?(.+?)((?:（| ).*）?)"
		# pattern = "(?:委托|赠文|无偿)(?::|：|;|；|,|，|。|-|-\s)?(.+)"
		
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
def formatTextIndent(text: str) -> str:
	text = text.replace("\r\n", "\n")       # CR 转 CRLF
	text = text.replace("\r", "\n")         # CR 转 CRLF
	space = """
		 
		​
		零宽不连字    通用标点 ‌
		零宽连字        通用标点 ‍
		窄式不换行空格 通用标点  
		中数学空格     通用标点	 
		文字连接符    通用标点	⁠
		零宽不换行空格（Zero Width No-Break Space） ﻿
		"""
	pattern = "[ ​﻿     ]"
	text = re.sub(pattern, "", text)
	text = re.sub("\n +", "\n", text)         # 删除段首半角空格
	text = re.sub("\n　+", "\n", text)        # 删除段首全角空格
	text = re.sub("\n{3,}", "\n\n\n", text)  # 删除多余空行
	return text
	
	
@checkNone
def formatTextPunctuation(text: str) -> str:
	text = re.sub("\\.{3,}", "…", text)  # 省略号标准化
	text = re.sub("。。。{3,}", "……", text)
	text = re.sub("!{3,}", "!!!", text)  # 感叹号标准化
	text = re.sub("！{3,}", "！！！", text)
	return text


@checkNone
def formatPixivText(text: str) -> str:
	# 处理 Pixiv 标识符 [newpage]
	text = text.replace("[newpage]", "\n\n")
	
	# [chapter: 章节名称]
	if "[chapter:" in text:
		a = re.findall("\\[chapter:(.*)]", text)
		for i in range(len(a)):
			string = a[i]
			if "第" in string and "章" in string:
				string = string.replace("章", "节")
			elif re.search("\\d+", string):
				string = f"第{string}节"
			elif re.search("[二三四五六七八九]?十?[一二三四五六七八九十]", string):
				string = f"第{string}节"
			else:
				string = f"第{i + 1}节 {string}"
			text = re.sub("\\[chapter:(.*)]", string, text, 1)
	
	# [jump: 链接目标的页面编号]
	if "[jump:" in text:
		a = re.findall("\\[jump:(.*)]", text)
		for i in range(len(a)):
			string = a[i]
			string = f"跳转至第{string}节"
			text = re.sub("\\[jump:(.*)]", string, text, 1)
	
	# [pixivimage: 作品ID]
	if "[pixivimage:" in text:
		a = re.findall("\\[pixivimage: (.*)]", text)
		for i in range(len(a)):
			string = a[i].strip(" ")
			string = f"插图：https://www.pixiv.net/artworks/{string}"
			text = re.sub("\\[pixivimage:(.*)]", string, text, 1)
	
	# [[jumpuri: 标题 > 链接目标的URL]]
	if "[jumpuri:" in text:
		a = re.findall("\\[{2}jumpuri: *(.*) *> *(.*)]{2}", text)
		for i in range(len(a)):
			name = a[i][0]
			link = a[i][1]
			if link in name:
				text = re.sub("\\[{2}jumpuri: *(.*) *> *(.*)]{2}", link, text, 1)
			else:
				string = f"{name}【{link}】"
				text = re.sub("\\[{2}jumpuri: *(.*) *> *(.*)]{2}", string, text, 1)
				
	# [uploadedimage: 上传图片自动生成的ID] 会被 pixivpy 转换
	if "If you would like to view illustrations" in text:
		pattern = "If you would like to view illustrations, please use your desktop browser."
		string = "【本文内有插图，请在 Pixiv 查看】\n"
		text = re.sub(pattern, string, text)
	# print(text)
	return text
	
	
@checkNone
def formatCaption(text: str) -> str:
	text = text.replace("<br>", "\n").replace("<br />", "\n")
	text = text.replace("<strong>", "").replace("</strong>", "")
	text = unescape(text)
	text = formatTextIndent(text)
	text = formatTextPunctuation(text)
	
	if "illust" in text or "novel" in text or "user" in text:
		# <a href="pixiv://illusts/12345">illust/12345</a>
		# <a href="pixiv://novels/12345">novel/12345</a>
		# <a href="pixiv://users/12345">user/12345</a>
		
		# pattern = r'<a href="pixiv://[illusts,novels,users]/[0-9]{5,}">[illust,novel,user]/[0-9]{5,}</a>'  # 无效写法
		pattern = r'<a href="pixiv://(?:illusts|novels|users)/[0-9]{5,}">(?:illust|novel|user)/[0-9]{5,}</a>'
		for string in re.findall(pattern, text):
			id = re.search("[0-9]{5,}", string).group()
			if "illust" in text:
				link = f"https://www.pixiv.net/artworks/{id}"
			elif "novel" in text:
				link = f"https://www.pixiv.net/novel/show.php?id={id}"
			elif "user" in text:
				link = f"https://www.pixiv.net/users/{id}"
			else:
				link = ""
			text = text.replace(string, link)
			
	if "target" in text:  # 一般a标签
		# <a href="https://deadmanshand.fanbox.cc/" target="_blank">https://deadmanshand.fanbox.cc/</a>
		pattern = '''<a href="(https://.*)" target=(?:'|")_blank(?:'|").*>https://.*</a>'''
		for link in re.findall(pattern, text):
			text = re.sub(pattern, link, text, 1)
	# print(text)
	return text


# def formatText(text: str, lang:str) -> str:
def formatText(text: str, lang="zh") -> str:
	text = f"\n{text}"
	text = formatTextIndent(text)
	text = formatPixivText(text)
	text = formatTextPunctuation(text)
	if lang in cjklist:                       # 中文格式
		text = re.sub("\n", "\n　　", text)    # 添加2个全角空格
	elif lang in eulist:                      # 英文格式
		text = re.sub("\n", "\n    ", text)   # 添加4个半角空格
	return text
	
	
def test():
	pass
	
	
if __name__ == '__main__':
	# testMode = 1
	if testMode:
		test()
	
	