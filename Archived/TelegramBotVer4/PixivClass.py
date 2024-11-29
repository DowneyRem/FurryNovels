#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import math
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from threading import Thread
from ssl import SSLError
from urllib.parse import unquote
import urllib3.exceptions
import requests.exceptions
import pixivpy3.utils

import numpy as np

from FileOperate import saveText, zipFile, openFile, removeFile, timer
from GetLanguage import getLanguage, getLangSystem
from PrintInfo import getFormattedTags, getInfoFromText
from TextFormat import formatNovelName, formatCaption, formatText
from TokenRoundRobin import TokenRoundRobin
from Translate import translate, transWords, transPath
from FurryNovelWeb import getOriginalLink, getUrl, getId
from configuration import novel_folder, illust_folder, addTranslatedTags, testMode


sys.dont_write_bytecode = True
_TEST_WRITE = False
# tokenPool = TokenRoundRobin()


def tokenPoolInit():
	global tokenPool
	# tokenPool = TokenRoundRobin()
	try:
		tokenPool = TokenRoundRobin()
	except RuntimeError as e:
		print(e)
		logging.critical(f"{e}")
		return
	

def checkNone(fun):
	@wraps(fun)
	def wrapper(*args, **kwargs):
		try:
			result = fun(*args, **kwargs)
			if result is not None:
				# print(result)
				return result
			else:
				raise ValueError
		except SSLError as e:
			logging.critical(f"SSLError{e}")
			logging.critical("请检测网络/代理/RefreshTokens 是否可用")
			return
		except ValueError:
			logging.warning('None Value')
			return
		except AttributeError as e:  # 'NoneType' object has no attribute 'title'
			logging.critical(f"AttributeError:{e}")
			logging.critical("网络/代理/Refresh Tokens 不可用；或请求频率过高")
			return
		except TypeError as e:  # 'NoneType' object is not callable
			logging.critical(f"TypeError: {e}")
			logging.critical("网络/代理/Refresh Tokens 不可用；或请求频率过高2")
			return
		except KeyboardInterrupt as e:
			logging.debug(e)
		except Exception as e:
			logging.error(e)
			return
	return wrapper


class PixivABC(ABC):
	link = ""          # 传入链接
	novel_id = 0       # 小说 ID
	novel_url = ""     # 小说网址
	novel_name = ""
	
	illust_id = 0      # 插画 ID
	illust_url = ""    # 插画网址
	illust_name = ""
	medium_urls = []   # 压缩链接
	original_urls = [] # 原图链接
	
	title = ""         # 标题
	tags = set[str]()  # tags
	caption = ""       # Caption
	text = ""          # 小说文本
	date = ""          # 创建日期
	pages = 0          # 页面数
	characters = 0     # 字数
	
	views = 0      # 点击数
	bookmarks = 0  # 收藏数
	comments = 0   # 评论数
	
	author_id = 0      # 作者 ID
	author_url = ""
	author_name = ""   # 作者名字
	author_icon = ""
	
	series_id = 0      # (所属)系列的 ID
	series_url = ""
	series_name = ""   # 系列名字
	count = 0          # 系列内篇数
	
	
	@abstractmethod    # 所有子类必须实现的方法
	def getJson(self):
		pass
	
	@abstractmethod
	def checkJson(self):
		pass
	
	@abstractmethod
	def getInfo(self):
		pass
	
	def getScore(self):
		pass
	
	@abstractmethod
	def __str__(self):
		pass
	
	def __repr__(self):
		pass
	
	@abstractmethod
	def setLinkInfo(self):
		pass
	
	def getNovelsList(self):
		pass
	
	def getText(self):
		pass
	
	def getLang(self):
		pass
	
	def setFileHead(self):
		pass
	
	@abstractmethod
	def save(self):
		pass
	
	def setFileInfo(self):
		pass
	
	def getTokenTimes(self):
		pass
	
	
class PixivBase(PixivABC):  # 共用方法
	views = 0      # 点击数
	bookmarks = 0  # 收藏数
	comments = 0   # 评论数
	rate = 0       # 收藏率
	score = -100   # 推荐指数
	
	novels_list_all = list[int]()  # 所有小说的 ID
	novels_list = list[int]()      # 所有可见小说的 ID
	novels_name = list[str]()      # 所有可见小说名称
	novels_caption = list[str]()   # 系列所有可见小说 capithon
	single_list = list[int]()      # 无系列小说 ID
	series_list = list[int]()      # 全部系列 ID
	lang = ""                      # 小说语言
	
	title = ""         # 标题
	author_name = ""   # 作者名字
	novel_url = ""     # 小说网址
	tags = set[str]()  # tags
	caption = ""       # Caption
	info = ""          # __str__()
	link_info = ""     # 发送链接后的信息 setLinkInfo()
	file_head = ""     # 小说文件头部信息 setFileHead()
	
	file_path = ""       # 小说文件路径
	file_text = ""       # 小说文件文本
	# tags = set[str]()  # tags
	file_info = ""       # 下载后，上传Telegram的信息 setFileInfo()
	furry = 0
	
	trans_path = ""      # 翻译文件路径
	trans_text = ""      # 翻译文件文本
	trans_tags = set[str]()
	trans_info = ""      # 上传Telegram的翻译信息
	furry2 = 0
	
	
	@staticmethod
	def getTags(tagslist: list) -> set[str]:  # 处理 json.novel.tags
		tags = set()
		for tag in tagslist:
			pattern = r"[,./;:\|，。：；、]"
			stag = re.split(pattern, tag.name)
			if "中国語" in stag and "中文" in stag:
				pass  # 避免干扰语言标签
			elif len(stag) >= 2:  # 添加拆分后标签
				tags.update(stag)
			elif "R-18" in tag.name:  # R18,R18G 规范化
				tags.add(tag.name.replace("-", ""))
			else:
				tags.add(tag.name)
				
			if tag.translated_name and addTranslatedTags:
				tags.add(tag.translated_name)
		return tags
	
	
	def addTags(self, novel: any):  # 处理 json.novel
		dic = {
			0: "SFW",
			1: "R18",
			2: "R18G"
		}
		self.tags = set()
		self.tags.add(dic[novel.x_restrict])
		if novel.visible:  # visible==False, 标签为空，可获取 x_restrict
			self.tags.update(self.getTags(novel.tags))
			
			
	def addNovelsList(self, novel: any):  # 处理 json.novel
		self.novels_list_all.append(novel.id)
		if novel.visible:  # visible==False, 只能获取ID
			self.novels_list.append(novel.id)
			self.novels_name.append(novel.title)
			self.novels_caption.append(novel.caption)
	
	
	def addSeriesList(self, novel: any):  # 处理 json.novel
		if not novel.series.id:  # visible==False, 可获取seriesID
			self.single_list.append(novel.id)
		elif novel.series.id not in self.series_list:
			self.series_list.append(novel.series.id)
	
	
	def checkTags(self) -> set:
		if ("R18" in self.tags or "R18G" in self.tags) and "SFW" in self.tags:
			self.tags.remove("SFW")
		# if "R18" in self.tags and "R18G" in self.tags:
		# 	self.tags.remove("R18")
		
		if "zh" in self.tags and "zh_cn" in self.tags:
			self.tags.remove("zh")
		elif "zh" in self.tags and "zh_tw" in self.tags:
			self.tags.remove("zh")
		elif "zh_cn" in self.tags and "zh_tw" in self.tags:
			self.tags.remove("zh_cn")
			self.tags.remove("zh_tw")
			self.tags.add(self.lang)
		return self.tags
	
	
	def formatTags(self) -> str:
		self.checkTags()
		tags = list(self.tags)
		if tags:
			if "#" in tags[0]:
				tags = " ".join(tags)  # 有#直接间断
			else:
				tags = f"#{' #'.join(tags)}"  # 无#逐个添加
		else:
			tags = ""
		return tags.replace("# ", "")
	
	
	def getAuthorInfo(self, obj):
		self.author_id = obj.user.id
		self.author_url = f"https://www.pixiv.net/users/{self.author_id}"
		self.author_name = obj.user.name
		self.author_icon = obj.user.profile_image_urls.medium
		
	
	def getScore(self) -> float:
		self.score = 0
		if self.views:  # 计算收藏率
			self.rate = 100 * self.bookmarks / self.views
		# print(self.views, self.bookmarks, self.comments, round(self.rate, 2))
		
		if self.views:  # 根据阅读量和收藏率增加推荐指数
			nums = []; a = -7.75; step1 = 1; step2 = 0.75
			for a in np.arange(a, a + 9 * step1, step1):  # 生成首列数据
				b = np.arange(a, a + 21 * step2, step2)   # 生成首行数据
				nums.append(list(b))
			nums = np.asarray(nums)
			# print(nums)
			
			x = int(self.views // 500)
			y = int(self.rate // 0.5)
			if x >= len(nums):
				x = len(nums) - 1
			if y >= len(nums[0]):
				y = len(nums[0]) - 1
			self.score += nums[x, y]
			# print(nums[x,y])
		
		if self.comments >= 1:  # 根据评论量增加推荐指数
			i = math.log2(self.comments)
			self.score += round(i, 2)
			
		if self.views <= 1000:  # 对阅读量小于1000的小说适当提高要求
			self.score += -0.75
		logging.info(f"【{self.title}】推荐指数：{self.score:.2f}")
		# print(f"推荐指数：{sore:.2f}")
		return round(self.score, 2)
	
	
	def getLang(self, force_update=False) -> str:
		if self.lang and not force_update:
			return self.lang
		if not self.novels_list_all:
			self.getNovelsList()
		
		text = []
		text.extend(self.novels_name)
		text.extend(self.novels_caption)
		self.lang = getLanguage("".join(text))
		self.tags.add(self.lang)
		return self.lang
	
	
	def __repr__(self) -> str:
		return f"{self.__class__.__name__}('{self.link}')"
	
	
	def setLinkInfo(self) -> str:   # 发送链接后的文本
		return f"未实现：{self.__class__.__name__}.setLinkInfo()"
	
	
	def setFileHead(self) -> str:  # 写入文件的信息
		if not self.lang:
			self.lang = getLanguage(self.title + self.caption)
		
		author = transWords("author", self.lang) + f"{self.author_name}\n"
		url = transWords("url", self.lang) + f"{self.novel_url}\n"
		tags = self.formatTags()
		tags = transWords("hashtags", self.lang) + f"{tags}\n"
		if self.caption:
			self.caption = transWords("others", self.lang) + f"{self.caption}\n"
		
		if self.count >= 1:  # 系列提示
			print(f"【{self.title}】，共有{self.count}章")
		self.file_head = f"{self.title}\n{author}{url}{tags}{self.caption}"
		# print(self.file_head)
		return self.file_head
	
	
	def setFileInfo(self, lang2="") -> tuple[str, str]:  # 上传文件至 Telegram 的信息
		self.file_info, self.furry = getInfoFromText(self.file_text, self.tags, self.lang)
		logging.info(f"【{self.title}】福瑞指数：{self.furry:.1f}")
		
		if lang2 and self.trans_text:
			self.trans_info, self.furry2 = getInfoFromText(self.trans_text, self.trans_tags, lang2)
		if __name__ == "__main__":  # 直接运行时输出上传 Telegram 的信息
			if self.trans_path:
				print(self.file_info, self.trans_info, sep="\n\n")
			else:
				print(self.file_info, sep="\n\n")
		return self.file_info, self.trans_info
	
	
	def checkLanguage(self):
		if "zh" in self.file_info and "zh_cn" in self.file_info:
			pass
		if "zh" in self.file_info and "zh_tw" in self.file_info:
			pass
		if "zh_cn" in self.file_info and "zh_tw" in self.file_info:
			pass
	
	
class PixivNovels(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	original_text = ""  # 未格式化文本
	
	
	def __init__(self, link: [int, str]):
		self.link = link
		self.novel_id = getId(link)
		self.novel_url = f"https://www.pixiv.net/novel/show.php?id={self.novel_id}"
		self.json = self.getJson()
		self.checkJson()
	
	
	@checkNone
	def getJson(self, force_update=False):
		if self._is_json_retrieved and not force_update:
			return self._original_json
		
		self._original_json = tokenPool.getAPI().novel_detail(self.novel_id)
		self._is_json_retrieved = True
		# print(self._original_json)
		return self._original_json
	
	
	def checkJson(self):
		if not self.json:
			raise RuntimeError("网络状态不佳，请稍后再次尝试")
		
		try:
			# {'error': {'user_message': 'The creator has limited who can view this content', 'message': '', 'reason': '', 'user_message_details': {}}}
			if self.json.error.user_message:
				raise ValueError("小说ID不存在，或已被删除")
			# {'error': {'user_message': '', 'message': 'Error occurred at the OAuth process. Please check your Access Token to fix this. Error Message: invalid_grant'}
			elif self.json.error.message:  # 排除已删除/不可见小说
				raise RuntimeError("Tokens 已失效，请稍后再次尝试")
			
		except AttributeError:  # 非正常小说，才有 error 信息
			# "visible": false, "is_mypixiv_only": true
			if self.json.novel.is_mypixiv_only:
				raise ValueError("该小说仅好P友可见，无法下载")
			# "visible": false, "is_mypixiv_only": false
			elif not self.json.novel.visible:
				raise ValueError("该小说未公开，无法下载")
			else:  # 正常小说
				self.getInfo()
	
	
	def getInfo(self) -> None:
		novel = self.json.novel
		self.title = self.novel_name = formatNovelName(novel.title)
		self.addTags(novel)
		self.checkTags()
		self.caption = formatCaption(novel.caption)
		self.date = f"{novel.create_date[0:10]} {novel.create_date[11:19]}"
		self.pages = novel.page_count
		self.characters = novel.text_length
		
		self.views = novel.total_view
		self.bookmarks = novel.total_bookmarks
		self.comments = novel.total_comments
		self.score = self.getScore()
		
		self.getAuthorInfo(novel)
		self.series_id = novel.series.id
		if self.series_id:
			self.series_url = f"https://www.pixiv.net/novel/series/{self.series_id}"
		self.series_name = novel.series.title
	
	
	@checkNone
	def getText(self, force_update=False) -> str:
		if self.original_text and force_update:
			return self.original_text
		
		if self.json.novel.visible:  # 排除不可见小说
			json = tokenPool.getAPI().novel_text(self.novel_id)
			self.original_text = json.novel_text
		return self.original_text
	
	
	def getLang(self, force_update=False) -> str:
		if self.lang and not force_update:
			return self.lang
		
		if not self.original_text:
			self.lang = getLanguage(f"{self.title}{self.author_name}{self.caption}")
		else:
			self.lang = getLanguage(self.original_text)
		self.tags.add(self.lang)
		return self.lang
	
	
	def __str__(self) -> str:
		tags = self.formatTags()
		self.info = f"{self.title} By {self.author_name}\n" \
			f"阅读：{self.views}；收藏：{self.bookmarks}；评论：{self.comments}；" \
			f"推荐指数：{self.score}；福瑞指数：{self.furry}\n标签：{tags}\n" \
			f"{self.novel_url}\n"
		return self.info
		
	
	def setLinkInfo(self) -> str:
		tags = self.formatTags()
		self.link_info = f"{self.title}\n作者：{self.author_name}\n标签：{tags}\n"
		
		if self.series_id:
			series = PixivSeries(self.series_id)
			self.link_info += f"\n{series.title}，共{series.count}篇\n"
			if series.checkCommission():
				self.link_info += "这可能是一篇委托小说，推荐下载txt单章或zip合集\n"
			else:
				self.link_info += "这可能是长篇小说的其中一章，推荐下载txt合集\n"
		# print(self.link_info)
		return self.link_info
	
	
	def saveNovel(self, author="", series="", i=0, lang="", lang2="") -> tuple:
		if not self.original_text:
			self.getText()
		if lang:
			self.lang = lang
		else:
			self.getLang()
		
		if author and series and i:  # 优化 SaveAuthor 调用 SaveAsZip & 单篇下载
			self.file_path = os.path.join(novel_folder, author, series, f"{i:0>2d} {self.title}.txt")
		elif series and i:  # 优化 SaveAsZip
			self.file_path = os.path.join(novel_folder, series, f"{i:0>2d} {self.title}.txt")
		else:   # 优化 SaveNovel
			self.file_path = os.path.join(novel_folder, f"{self.title}.txt")
		print(self.file_path)
		
		self.text = formatText(self.original_text, self.lang)
		self.file_head = self.setFileHead()
		self.file_text = f"{self.file_head}\n\n{self.text}"
		saveText(self.file_path, self.file_text)
		
		if lang2 and self.lang != lang2:
			self.trans_tags = self.tags.copy()
			self.trans_tags.discard(self.lang)
			self.trans_tags.update([lang2, "translated"])
			# print(self.tags, self.trans_tags, sep="\n")
			
			self.trans_path = transPath(self.file_path, mode=0, lang1=self.lang, lang2=lang2)
			self.trans_text = translate(self.file_text, lang1=self.lang, lang2=lang2)
			saveText(self.trans_path, self.trans_text)
			print(self.trans_path)
		
		if not author and not series:  # 直接运行时
			self.setFileInfo(lang2=lang2)
		return self.file_path, self.trans_path
	
	
	def save(self, lang2="") -> tuple[str, str]:
		return self.saveNovel(lang2=lang2)
	
	
	def getTokenTimes(self) -> int:
		a = 0       # 初始化
		b = 1       # getInfo
		c = 1 + b   # getText
		print(a, b, c)
		return c


class PixivIllusts(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	type = ""  # illust/manga
	is_ai_generated = 0
	folder = ""
	files = []
	zippath = ""
	
	
	def __init__(self, link: [int, str]):
		self.link = link
		self.illust_id = getId(link)
		self.illust_url = f"https://www.pixiv.net/artworks/{self.illust_id}"
		self.json = self.getJson()
		self.checkJson()
	
	
	@checkNone
	def getJson(self, force_update=False):
		if self._is_json_retrieved and not force_update:
			return self._original_json
		
		self._original_json = tokenPool.getAPI().illust_detail(self.illust_id)
		self._is_json_retrieved = True
		# print(json.dumps(self._original_json, ensure_ascii=False))
		return self._original_json
	
	
	def checkJson(self):
		if not self.json:
			raise RuntimeError("网络状态不佳，请稍后再次尝试")
		
		try:
			# {'error': {'user_message': 'The creator has limited who can view this content', 'message': '', 'reason': '', 'user_message_details': {}}}
			if self.json.error.user_message:
				raise ValueError("插画ID不存在，或已被删除")
			# {'error': {'user_message': '', 'message': 'Error occurred at the OAuth process. Please check your Access Token to fix this. Error Message: invalid_grant'}
			elif self.json.error.message:  # 排除已删除/不可见小说
				raise RuntimeError("Tokens 已失效，请稍后再次尝试")
		
		except AttributeError:  # 非正常小说，才有 error 信息
			# "visible": false, "is_mypixiv_only": true
			if self.json.illust.is_mypixiv_only:
				raise ValueError("该插画仅好P友可见，无法下载")
			# "visible": false, "is_mypixiv_only": false
			elif not self.json.illust.visible:
				raise ValueError("该插画未公开，无法下载")
			else:  # 正常小说
				self.getInfo()
	
	
	def getInfo(self):
		illust = self.json.illust
		self.title = self.illust_name = formatNovelName(illust.title)
		self.addTags(illust)
		self.caption = formatCaption(illust.caption)
		self.date = f"{illust.create_date[0:10]} {illust.create_date[11:19]}"
		self.type = illust.type
		self.original_urls, self.medium_urls = [], []  # 清空源链接
		self.pages = illust.page_count  # 插画张数
		if self.pages >= 2:
			for image_urls in illust.meta_pages:
				self.original_urls.append(image_urls.image_urls.original)
				self.medium_urls.append(image_urls.image_urls.medium)
		else:
			self.original_urls.append(illust.meta_single_page.original_image_url)
			self.medium_urls.append(illust.image_urls.medium)
		
		self.views = illust.total_view
		self.bookmarks = illust.total_bookmarks
		self.comments = illust.total_comments
		self.score = self.getScore()
		
		self.getAuthorInfo(illust)
		if self.type == "manga":
			self.series_id = illust.series.id
			self.series_url = f"https://www.pixiv.net/user/{self.author_id}/series/{self.series_id}"
			self.series_name = illust.series.title
		self.is_ai_generated = not illust.illust_ai_type
		
	
	def __str__(self):
		self.info = f"{self.title}\nBy {self.author_name}\n" \
			f"阅读：{self.views}；收藏：{self.bookmarks}；评论：{self.comments}\n" \
			f"标签：{self.formatTags()}\n{self.illust_url}\n"
		return self.info
	
	
	def setLinkInfo(self) -> str:
		return self.__str__()
	
	
	def save(self, lang2=""):
		self.folder = os.path.join(illust_folder, self.title)
		removeFile(self.folder)
		os.makedirs(self.folder)
		# print(f"{self.folder=}")
		self.files = []  # 清空下载图片路径
		for i in range(0, len(self.original_urls)):
			tokenPool.getAPI().download(self.original_urls[i], path=self.folder, name=f"{self.title}{i+1}.jpg")  # todo 报错，无法下载
			self.file_path = os.path.join(self.folder, f"{self.title}{i+1}.jpg")
			self.files.append(self.file_path)
		return self.files
	
	
	def saveAsZip(self, password=""):
		self.files = self.save()
		self.zippath = zipFile(self.folder, password=password)
		return self.zippath
	

class PixivSeries(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	
	series_id = 0        # 系列的 ID
	series_url = ""
	series_name = ""     # 系列名字
	count = 0            # 系列内的小说篇数
	
	novels_list_all = list[int]()  # 系列所有小说的 ID
	novels_list = list[int]()      # 系列所有可见小说的 ID
	novels_name = list[str]()      # 系列所有可见小说名称
	novels_caption = list[str]()   # 系列所有可见小说 capithon
	commission = None              # 默认非委托系列
	lang = ""                      # 系列语言
	
	tags = set[str]()    # 系列所有可见小说的 tags
	tags30 = set[str]()  # 系列前30小说的 tags
	
	novel_id = 0      # 系列第1篇小说的 ID
	novel_url = ""    # 系列第1篇小说的网址
	novel_name = ""   # 系列第1篇小说名称
	
	
	def __init__(self, link: [int, str]):
		self.link = link
		self.series_id = getId(link)
		self.series_url = f"https://www.pixiv.net/novel/series/{self.series_id}"
		self.json = self.getJson()  # 原始数据
		self.checkJson()
	
	
	@checkNone
	def getJson(self, force_update=False) -> any:
		if self._is_json_retrieved and not force_update:
			return self._original_json
		
		self._original_json = tokenPool.getAPI().novel_series(self.series_id, last_order=None)
		self._is_json_retrieved = True
		# print(self._original_json)
		return self._original_json
	
	
	def checkJson(self):
		if not self.json:
			raise RuntimeError("网络状态不佳，请稍后再次尝试")
		
		try:
			# {'error': {'user_message': 'This series no longer exists. It may have been deleted. Please check the series ID.', 'message': '', 'reason': '', 'user_message_details': {}}}
			if self.json.error.user_message:  # 排除已删除系列
				raise ValueError("系列ID不存在，或已被删除")
			# {'error': {'user_message': '', 'message': 'Error occurred at the OAuth process. Please check your Access Token to fix this. Error Message: invalid_grant'}
			elif self.json.error.message:  # 排除已删除/不可见小说
				raise RuntimeError("Tokens 已失效，请稍后再次尝试")
			
		except AttributeError:  # 非正常小说，才有 error 信息
			self.getInfo()
	
	
	def getInfo(self) -> None:
		series = self.json.novel_series_detail
		self.title = self.series_name = formatNovelName(series.title)  # 系列标题
		# if series.is_concluded == 0:
		# 	self.tags.add("Unfinished")
		self.caption = formatCaption(series.caption)  # 系列简介
		self.count = series.content_count  # 系列内小说数
		self.characters = series.total_character_count # 系列总字数
		self.getAuthorInfo(series)
		
		novel = self.json.novel_series_first_novel   # 系列第1篇小说
		self.novel_id = novel.id
		self.novel_url = f"https://www.pixiv.net/novel/show.php?id={self.novel_id}"
		self.novel_name = formatNovelName(novel.title)
		
		self.views = novel.total_view
		self.bookmarks = novel.total_bookmarks
		self.comments = novel.total_comments
		self.score = self.getScore()
		if self.count <= 30:
			self.getFirst30NovelsList()
			
	
	def getFirst30NovelsList(self) -> None:  # 获取前三十小说id和标签
		for novel in self.json.novels:
			self.addNovelsList(novel)
			self.addTags(novel)
		self.checkTags()
	
	
	def __str__(self) -> str:
		if not self.tags:
			self.getFirst30NovelsList()
			
		tags = self.formatTags()
		self.info = f"{self.title}  By {self.author_name}\n{self.caption}\n{tags}\n{self.series_url}\n{self.novel_url}"
		return self.info
		
	
	def setLinkInfo(self) -> str:
		self.link_info = f"系列：{self.title}，共{self.count}篇\n作者：{self.author_name}\n{self.caption}\n\n"
		if self.checkCommission():
			self.link_info += "这可能是一个委托合集，推荐下载为zip合集"
		else:
			self.link_info += "这可能是一篇长篇小说，推荐下载为txt合集"
		return self.link_info
	
	
	def getNovelsList(self, force_update=False) -> None:
		if self.novels_list and self.tags and not force_update:
			return
		
		def addList(json: any):
			for novel in json.novels:
				self.addTags(novel)
				self.addNovelsList(novel)
		self.tags = set()   # 第二次下载时，清空原有内容
		self.novels_list_all, self.novels_list = [], []
		self.novels_name, self.novels_caption = [], []
		
		addList(self.getJson())
		if len(self.novels_list_all) >= 30:  # 1次最多可请求到30个id
			next_qs = tokenPool.getAPI().parse_qs(self.json.next_url)
			while next_qs is not None:
				json = tokenPool.getAPI().novel_series(**next_qs)
				addList(json)
				next_qs = tokenPool.getAPI().parse_qs(json.next_url)
		self.checkTags()
		
		visible_count = len(self.novels_list)
		if not visible_count:
			raise ValueError(f"{self.title} 全部 {self.count} 篇小说均有限制，不可下载")
		elif self.count > visible_count:
			print(f"{self.title} 有 {self.count - visible_count} 篇小说，无权限下载")
			print(f"正在下载 {visible_count} 篇小说")
		# print(len(self.novels_list), len(self.tags))
		# print(self.novels_list, self.novels_names, self.novels_captions, self.tags, sep="\n")
	
	
	def checkCommission(self) -> bool:
		if self.commission is not None:
			return self.commission
		
		if not self.novels_list:
			self.getNovelsList()
		text = []  # 计算委托出现次数
		text.extend([self.title, self.caption])
		text.extend(self.novels_name)
		text.extend(self.novels_caption)
		text = " ".join(text)
		times = text.count("委托") + text.count("约稿") + text.count("約稿") + text.count("commission")
		
		if times >= 0.2 * len(self.novels_list):
			self.commission = True
			self.tags.add("Commission")
		else:
			self.commission = False
			self.tags.add("Series")
		return self.commission
	
	
	@timer
	def saveAsZip(self, author="", lang="", lang2="") -> tuple:
		print(f"SaveAsZip: {self.title}")
		logging.info(f"SaveAsZip: {self.title}")
		if not self.novels_list:
			self.getNovelsList()
			self.checkCommission()
		if lang:
			self.lang = lang
		
		path1, path2 = "", ""
		for i in range(len(self.novels_list)):
			try:
				novel = PixivNovels(self.novels_list[i])
				(path1, path2) = novel.saveNovel(author, self.title, i+1, self.lang, lang2)
				self.tags.update(novel.tags)
				if not lang:
					self.lang = novel.lang
			except ValueError as e:
				print(e)
				logging.error(e)
		self.file_path = os.path.dirname(path1)
		
		if lang2 and self.lang != lang2:
			self.trans_path = os.path.dirname(path2)  # 直接运行时，父文件夹即是翻译文件夹
			self.trans_tags = self.tags.copy()
			self.trans_tags.discard(self.lang)
			self.trans_tags.update([lang2, "translated"])
			# print(self.tags, self.trans_tags, sep="\n")
			
		if not author:  # 直接运行时
			self.file_path = zipFile(self.file_path)
			if self.trans_path:  # 压缩翻译目录
				self.trans_path = zipFile(self.trans_path)
			self.setFileInfoForZip(lang2=lang2)
		return self.file_path, self.trans_path
	
	
	@timer
	def saveAsTxt(self, author="", lang="", lang2="") -> tuple:
		print(f"SaveAsTxt: {self.title}")
		logging.info(f"SaveAsTxt: {self.title}")
		if not self.novels_list:
			self.getNovelsList()
			self.checkCommission()
		
		if author:  # SaveAuthor 优化
			self.file_path = os.path.join(novel_folder, author, f"{self.title}.txt")
		else:       # SaveAsTxt 优化
			self.file_path = os.path.join(novel_folder, f"{self.title}.txt")
		
		text = ""
		for i in range(len(self.novels_list)):
			novel_id = self.novels_list[i]
			try:
				novel = PixivNovels(novel_id)
				novel_title = novel.title
				novel_caption = novel.caption
				novel_text = novel.getText()
				self.tags.update(novel.tags)
				
			except ValueError as e:
				print(e)
				logging.error(e)
			else:
				novel_title_replaced = novel_title.replace(self.title, "").replace("-", "")
				if len(novel_title_replaced) >= 2:
					novel_title = novel_title_replaced
				if ("第" not in novel_title) and ("章" not in novel_title):
					novel_title = f"第{i+1}章 {novel_title}"
				print(novel_title)
				text += f"{novel_title}\n{novel_caption}\n\n{novel_text}\n\n\n"
			
		if lang:
			self.lang = lang
		else:
			self.lang = getLanguage(text)
			
		self.tags.add(self.lang)
		self.text = formatText(text, self.lang)
		self.file_text = f"{self.setFileHead()}\n\n{self.text}"
		saveText(self.file_path, self.file_text)
		print(self.file_path)
		
		if lang2 and self.lang != lang2:
			self.trans_tags = self.tags.copy()
			self.trans_tags.discard(self.lang)
			self.trans_tags.update([lang2, "translated"])
			# print(self.tags, self.trans_tags, sep="\n")
			
			self.trans_path = transPath(self.file_path, mode=0, lang1=self.lang, lang2=lang2)
			self.trans_text = translate(self.file_text, lang1=self.lang, lang2=lang2)
			saveText(self.trans_path, self.trans_text)
			print(self.trans_path)
		
		if not author:  # 直接运行时
			self.setFileInfo(lang2=lang2)
		return self.file_path, self.trans_path
	
	
	def setFileInfoForZip(self, lang2="") -> tuple[str, str]:  # 上传文件至 Telegram 的信息
		tags = getFormattedTags(self.tags)
		self.file_info = f"{self.title}\nBy #{self.author_name}\n{tags}\n{self.novel_url}"
		
		if lang2 and self.trans_path:
			title = os.path.splitext(os.path.basename(self.trans_path))[0]
			tags = getFormattedTags(self.trans_tags)
			self.trans_info = f"{title}\nBy #{self.author_name}\n{tags}\n{self.novel_url}"
		
		if __name__ == "__main__":  # 直接运行时输出上传 Telegram 的信息
			if self.trans_path:
				print(self.file_info, self.trans_info, sep="\n\n")
			else:
				print(self.file_info, sep="\n\n")
		return self.file_info, self.trans_info
	
	
	@timer
	def saveSeries(self, author="", lang="", lang2="") -> tuple[str, str]:
		self.getNovelsList(force_update=True)  # 强制更新
		if self.checkCommission():
			print("委托系列将下载成zip文件")
			paths = self.saveAsZip(author, lang, lang2)
		else:
			print("长篇小说将下载成txt文件")
			paths = self.saveAsTxt(author, lang, lang2)
		self.getTokenTimes()
		return paths
	
	
	def save(self, lang2=""):
		return self.saveSeries(lang2=lang2)
	
	
	def getTokenTimes(self) -> int:
		if not self.novels_list:
			self.getNovelsList()
			
		novels = len(self.novels_list)
		a = 1  # 创建PixivSeries 1个请求
		b = 2 * (novels // 30 + 1)   # getNovelList 与 getInfo 每30个小说2个请求
		c = 2 * novels + b + a       # saveSeries 每个小说2个请求
		print(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name} 预估下载请求次数为：{c}")
		return c


class PixivFakeSeries(PixivSeries):  # 自定义Series
	def __init__(self, links: [str, list]):  # 可处理小说网址或小说ID
		if isinstance(links, str) and "\n" in links:
			links = links.split()
		if isinstance(links, list):
			self.link = "\n".join(links)
			self.links = links
			self.commission = False  # 默认下载成 TXT
			self.getNovelsList(force_update=True)  # 检测 Series 链接，并入 self.novels_list
			self.count = len(self.novels_list)
			self.getInfo()
		
	
	def getInfo(self):
		self.novel_id = self.novels_list[0]    # 系列第1篇小说
		self.novel = PixivNovels(self.novel_id)
		self.novel_url = self.novel.novel_url
		self.novel_name = self.novel.novel_name
		self.title = self.series_name = re.sub(r"\d", "", self.novel_name)
		self.tags.update(self.novel.tags)
		self.caption = self.novel.caption
		self.characters += self.novel.characters
		# self.novel.getText()
		# self.lang = self.novel.getLang()

		self.views = self.novel.views
		self.bookmarks = self.novel.bookmarks
		self.comments = self.novel.comments
		self.score = self.getScore()
		
		self.author_id = self.novel.author_id
		self.author_name = self.novel.author_name
		self.author_url = self.novel.author_url
		
	
	def getNovelsList(self, force_update=False) -> None:
		if self.novels_list and not force_update:
			return
		
		self.novels_list = []
		for link in self.links:
			if "novel/series" in link:
				series = PixivSeries(link)
				series.getNovelsList(force_update=True)  # 强制更新
				self.novels_list.extend(series.novels_list)
			elif "novel" in link or "pn" in link:  # 去末尾s，兼容linpx
				self.novels_list.append(link)
				
	
	def __repr__(self) -> str:
		return f"{self.__class__.__name__}({self.link})"


	def saveAsTxt(self, author="", lang="", lang2="") -> tuple:
		return super().saveAsTxt(author, lang, lang2)
	
	
	def saveAsZip(self, author="", lang="", lang2="") -> tuple:
		return super().saveAsZip(author, lang, lang2)
	
	
	def setLinkInfo(self) -> str:
		return "将多个链接视为一个系列小说？"
		
	
	
class PixivManga(PixivBase):
	def __init__(self):
		pass
	
	
class PixivAuthor(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	
	author_id = 0     # 作者 ID
	author_url = ""
	author_name = ""  # 作者名字
	profile_url = ""  # 头像链接
	caption = ""      # 作者简介
	webpage = ""      # 主页链接
	twitter = ""      # 推特链接
	followers = 0     # 总关注者
	
	manga = 0
	illusts = 0
	illusts_series = 0
	novels = 0
	novels_series = 0
	
	novels_list_all = list[int]()   # 所有小说 ID
	novels_list = list[int]()       # 所有可见小说 ID
	single_list = list[int]()       # 无系列小说 ID
	series_list = list[int]()       # 全部系列 ID
	novel_id = 0                    # 最近1篇小说
	series_id = 0                   # 最近1篇系列小说
	
	novels_name = list[str]()       # 所有小说名称
	novels_caption = list[str]()    # 所有小说 capithon
	novels_data = list[str, int]()
	lang = ""        # 小说语言
	
	author_dir = ""  # 文件夹路径
	file_path = ""   # 文件路径
	file_info = ""
	trans_path = ""  # 翻译文件路径
	trans_info = ""
	
	
	def __init__(self, link: [int, str]):
		self.link = link
		self.author_id = getId(link)
		self.author_url = f"https://www.pixiv.net/users/{self.author_id}"
		self.json = self.getJson()
		self.checkJson()
	
	
	@checkNone
	def getJson(self, force_update=False) -> any:
		if self._is_json_retrieved and not force_update:
			return self._original_json
		
		self._original_json = tokenPool.getAPI().user_detail(self.author_id)
		self._is_json_retrieved = True
		# print(self._original_json)
		return self._original_json
	
	
	def checkJson(self):
		if not self.json:
			raise RuntimeError("网络状态不佳，请稍后再次尝试")
		
		try:
			# {'error': {'user_message': 'This series no longer exists. It may have been deleted. Please check the series ID.', 'message': '', 'reason': '', 'user_message_details': {}}}
			if self.json.error.user_message:  # 排除已删除系列
				raise ValueError("作者ID不存在，或已被删除")
			# {'error': {'user_message': '', 'message': 'Error occurred at the OAuth process. Please check your Access Token to fix this. Error Message: invalid_grant'}
			elif self.json.error.message:  # 排除已删除/不可见小说
				raise RuntimeError("Tokens 已失效，请稍后再次尝试")
			
		except AttributeError:  # 非正常小说，才有 error 信息
			self.getInfo()
	
	
	def getInfo(self) -> None:
		user = self.json.user
		self.title = self.author_name = formatNovelName(user.name)
		self.author_dir = os.path.join(novel_folder, self.author_name)
		self.profile_url = self.author_icon = user.profile_image_urls.medium  # Profile pic
		self.caption = formatCaption(user.comment)
		
		profile = self.json.profile
		self.illusts = profile.total_illusts + profile.total_manga
		self.illusts_series = profile.total_illust_series
		self.novels = profile.total_novels
		self.novels_series = profile.total_novel_series
		
		self.webpage = profile.webpage
		self.twitter = profile.twitter_url
		self.followers = profile.total_follow_users
	
	
	def __str__(self) -> str:
		self.info = f"#{self.author_name} ({self.author_id})\n{self.author_url}\n"
		if self.webpage:
			self.info += f"主页：{self.webpage}\n"
		if self.twitter:
			self.info += f"推特：{self.twitter}\n"
		
		if self.novels and self.single_list:
			single_novels = len(self.single_list)
			self.info += f"小说：{self.novels}篇：单篇：{single_novels}篇；" \
				f"系列：{self.novels_series}个共{self.novels - single_novels}篇\n"
		elif self.novels:
			self.info += f"小说：{self.novels}篇：系列：{self.novels_series}个\n"
			
		if self.illusts:
			self.info += f"插画：{self.illusts}幅；系列：{self.illusts_series}个\n"
		self.info = self.info.strip()
		# print(self.info)
		return self.info
	
	
	def setLinkInfo(self) -> str:
		self.link_info = f"{self.author_name}\n"
		if self.novels >= 1:
			self.link_info += f"小说：{self.novels}篇，系列：{self.novels_series}个\n"
		if self.illusts >= 1:
			self.link_info += f"插画：{self.illusts}幅，系列：{self.illusts_series}个\n"
		self.link_info = self.link_info.strip()
		# print(self.link_info)
		return self.link_info
		
	
	def getNovelsList(self, force_update=False) -> None:
		if (self.single_list or self.series_list) and not force_update:
			return
		
		def addList(json: any):
			for novel in json.novels:
				self.addTags(novel)
				self.addNovelsList(novel)
				self.addSeriesList(novel)
				
		self.tags = set()   # 第二次下载时，清空原有内容
		self.novels_list_all, self.novels_list = [], []
		self.novels_name, self.novels_caption = [], []
		self.single_list, self.series_list = [], []
		
		json = tokenPool.getAPI().user_novels(self.author_id)
		addList(json)
		if len(self.novels_list_all) >= 30:  # 1次最多可请求到30个id
			next_qs = tokenPool.getAPI().parse_qs(json.next_url)
			while next_qs is not None:
				json = tokenPool.getAPI().user_novels(**next_qs)
				addList(json)
				next_qs = tokenPool.getAPI().parse_qs(json.next_url)
		self.checkTags()
		
		self.novel_id = self.novels_list_all[0]   # 最近1篇小说
		try:
			self.series_id = self.series_list[0]  # 最近1篇系列小说
		except IndexError:
			self.series_id = 0
			
		self.count = len(self.novels_list_all)
		visible_count = len(self.novels_list)
		if not visible_count:
			raise ValueError(f"{self.title} 全部 {self.count} 篇小说均有限制，不可下载")
		elif self.count > visible_count:
			print(f"{self.title} 有 {self.count - visible_count} 篇小说，无权限下载")
			print(f"正在下载 {visible_count} 篇小说")
		# print(len(self.novels_list_all), len(self.single_list), len(self.series_list), sep="\n")
		# print(self.novels_list_all, self.single_list, self.series_list, self.tags, sep="\n")
		
	
	def makeAuthorDir(self) -> None:
		os.makedirs(self.author_dir, exist_ok=True)
	
	
	def saveAuthorIcon(self, force_update=False) -> str:
		self.makeAuthorDir()
		name = f"{self.author_name}.jpg"
		path = os.path.join(self.author_dir, name)
		if os.path.exists(path) and force_update:
			os.remove(path)
		elif os.path.exists(path):
			pass
		else:
			try:
				tokenPool.getAPI().download(self.profile_url, path=self.author_dir, name=name)
			except (ConnectionResetError, urllib3.exceptions.MaxRetryError, requests.exceptions.ProxyError, pixivpy3.utils.PixivError) as e:
				print("网络问题，无法下载作者头像")
				logging.error(e)  # 代理需支持UDP
			except Exception as e:
				logging.error(e)  # 代理需支持UDP
		
		if os.path.exists(path):
			print(f"作者头像：{path}")
		return path

	
	def saveAuthorInfo(self) -> str:
		self.makeAuthorDir()
		self.getLang()
		
		# 写入 info 当中的 li 指定的社交网站
		text = [self.author_name, f"{self.author_url}"]
		info = dict(self.json.user)
		info.update(dict(self.json.profile))
		li = "webpage twitter_url pawoo_url".split(" ")
		for item in li:
			if info[item]:
				text.append(f"{info[item]}")
		text.extend([self.caption.strip(), "", "", ])
		
		# workspace 不为空时添加"工作空间"及具体项目
		workspace = dict(self.json.workspace)
		for value in workspace.values():
			if value:
				text.append(transWords("workspace", self.lang))
				break
		for key in workspace:
			if workspace[key]:
				# text.append(f"{key}{workspace[key]}")  # 未翻译内容
				text.append(f"{transWords(key, self.lang)}{workspace[key]}")
		
		path = os.path.join(self.author_dir, f"{self.author_name}.txt")
		text = "\n".join(text)
		saveText(path, text)
		print(f"作者信息：{path}")
		return path
	
		
	@timer
	def saveAuthorNovels(self, lang2="") -> tuple:
		self.makeAuthorDir()
		self.getNovelsList()
		self.getLang()
		
		path1, path2, paths = "", "", []
		single = transWords("single", self.lang)
		for i in range(len(self.single_list)):
			try:
				novels = PixivNovels(self.single_list[i])
				path1, path2 = novels.saveNovel(self.author_name, single, i+1, self.lang, lang2)
			except ValueError as e:
				print(e)
				logging.error(e)
				
		for j in range(len(self.series_list)):
			try:
				series = PixivSeries(self.series_list[j])
				path1, path2 = series.saveSeries(self.author_name, self.lang, lang2)
			except ValueError as e:
				print(e)
				logging.error(e)
		self.file_path = zipFile(self.author_dir)
		
		if lang2 and self.lang != lang2:
			length = len(self.author_dir.split(os.sep))  # 构造翻译路径，../翻译/作者名/(系列名/单篇)/小说名
			trans_dir = os.sep.join(path2.split(os.sep)[:length + 1])
			self.trans_path = zipFile(trans_dir)
			# print(self.author_dir, self.trans_path, sep="\n")
			
		self.setFileInfo(lang2=lang2)
		return self.file_path, self.trans_path
	
	
	@timer
	def setFileInfo(self, lang2="") -> tuple[str, str]:  # 上传文件至 Telegram 的信息
		self.file_info = f"#{self.author_name} #ID{self.author_id} #{self.lang}\n"
		single_novels = len(self.single_list)
		if self.single_list:
			self.file_info += f"小说：{self.novels}篇：单篇：{single_novels}篇\n"
		if self.novels_series:
			self.file_info += f"系列：{self.novels_series}个，共{self.novels - single_novels}篇\n"
		self.file_info += f"{self.author_url}"
			
		if lang2:
			self.trans_info = translate(self.file_info, lang2=lang2, lang1=self.lang)
			self.trans_info = self.trans_info.replace(f"#{self.lang}", f"#{lang2}")
		if __name__ == "__main__":  # 直接运行时输出上传 Telegram 的信息
			if self.trans_path:
				print(f"\n{self.file_info}\n\n{self.trans_info}\n")
			else:
				print(f"\n{self.file_info}\n")
		return self.file_info, self.trans_info
	
	
	@timer
	def saveAuthor(self, lang2="") -> tuple:
		self.makeAuthorDir()
		self.getNovelsList()
		# self.getNovelsList(force_update=True)  # 已在 PixivObject 中强制更新
		self.getLang()
		self.saveAuthorIcon()
		self.saveAuthorInfo()
		paths = self.saveAuthorNovels(lang2=lang2)
		self.getTokenTimes()
		return paths
	
	
	def save(self, lang2="") -> tuple:
		return self.saveAuthor(lang2=lang2)
	
	
	def getNovelsData(self) -> list[list]:
		self.getNovelsList()
		self.novels_data = []
		for novel_id in self.novels_list_all:
			n = PixivNovels(novel_id)
			self.novels_data.append([n.title, n.date, n.characters, n.views, n.bookmarks, n.comments])
		# print(self.novel_data)
		return self.novels_data
	
	
	def getTokenTimes(self, precise=0) -> int:
		# precise 精确计算
		a = 1  # 默认 getinfo 1个请求
		b = 2 * (self.novels // 30 + 1) + a   # getNovelsList 每30个小说，2个请求
		num = 2 * self.novels + 2 * self.novels_series + b  # saveAuthor 每个小说2个请求，保守计算
		
		if precise:
			if not self.single_list:
				self.getNovelsList()
			
			num = 2 * len(self.single_list) + b
			for i in range(len(self.series_list)):
				num += PixivSeries(self.series_list[i]).getTokenTimes()
			print(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name} 预估下载请求次数为：{num}")
		else:
			print(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name} 略估下载请求次数为：{num}")
			
		if num >= 390:
			print(f"请求过多({num}次)，可能无法完全下载")
		return num


class PixivObject(object):
	url = ""          # 传入的 url
	novel_url = ""    # 小说 url
	illust_url = ""
	series_url = ""   # 系列小说 url
	author_url = ""   # 作者 url
	lang = ""
	tags = set[str]()  # tags
	
	novel_id = 0
	illust_id = 0
	series_id = 0
	author_id = 0
	score = 0
	
	file_path = ""   # 小说文件路径
	file_info = ""   # 上传Telegram的信息
	furry = 0
	trans_path = ""  # 翻译文件路径
	trans_info = ""  # 上传Telegram的翻译信息
	
	
	@staticmethod
	def addAttribute(function: callable):
		@wraps(function)
		def wrapper(self, *args, **kwargs):
			result = function(self, *args, **kwargs)
			self.file_path, self.trans_path = self.obj.file_path, self.obj.trans_path
			self.file_info, self.trans_info = self.obj.file_info, self.obj.trans_info
			self.score, self.furry = self.obj.score, self.obj.furry
			self.lang, self.tags = self.obj.lang, self.obj.tags
			return result
		return wrapper
	
	
	def __init__(self, string):
		self.obj = None
		if (isinstance(string, str) and "\n" in string) or isinstance(string, list):
			self.obj = PixivFakeSeries(string)
		
		elif isinstance(string, str):
			self._url = getUrl(string)  # 用于保留 furrynovel.com 的网址链接
			self.url = self._url
			self.factory()
			# 不可创建线程 AttributeError: 'PixivObject' object has no attribute 'obj'
			# t2 = Thread(target=PixivObject.factory, args=(self,))
			# t2.start()
			# t2.join()  # 不join AttributeError: 'PixivObject' object has no attribute 'obj'
	
	
	def factory(self):
		if "furrynovel.com" in self.url:
			self.url = getOriginalLink(self.url)
		if not self.url:
			raise ValueError(f"源网站已撤稿，无法获取其 Pixiv 小说 id")
		if "bilibili" in self.url:
			raise ValueError(f"暂不支持 bilibili 小说，请去源网站阅读\n{self._url}")
		
		if "user" in self.url:  # 去末尾s，兼容linpx
			self.obj = PixivAuthor(self.url)
			# self.obj.getNovelsList(force_update=True)  # 强制更新
		elif "user" in self.url and "series" in self.url:
			raise ValueError("输入链接有误，不支持漫画/插画系列")
		elif "novel/series" in self.url:
			self.obj = PixivSeries(self.url)
			# self.obj.getNovelsList(force_update=True)  # 强制更新
		elif "novel" in self.url or "pn" in self.url:  # 去末尾s，兼容linpx
			self.obj = PixivNovels(self.url)
		elif "artwork" in self.url:
			self.obj = PixivIllusts(self.url)
			self.illust_id = self.obj.illust_id
			self.illust_url = self.obj.illust_url
		else:
			raise ValueError("输入链接有误")
		
		self.novel_id = self.obj.novel_id
		self.series_id = self.obj.series_id
		self.author_id = self.obj.author_id
		self.author_name = self.obj.author_name
		self.novel_url = f"https://www.pixiv.net/novel/show.php?id={self.novel_id}"
		if self.series_id:
			self.series_url = f"https://www.pixiv.net/novel/series/{self.series_id}"
		self.author_url = f"https://www.pixiv.net/users/{self.author_id}"
		
	
	def __str__(self):
		return self.obj.__str__()
	
	
	def __repr__(self):
		return self.obj.__repr__()
	
	
	def setLinkInfo(self):
		return self.obj.setLinkInfo()
	
	
	def getTokenTimes(self, precise=0):
		if isinstance(self.obj, PixivAuthor):
			return self.obj.getTokenTimes(precise)
		else:
			return self.obj.getTokenTimes()
	
	
	@addAttribute
	def save(self, lang2=""):  # 默认下载
		print("开始下载……")
		return self.obj.save(lang2=lang2)
	
	
	@addAttribute
	def saveNovel(self, lang2=""):
		print("开始下载单章小说……")
		if not isinstance(self.obj, PixivNovels):
			self.obj = PixivNovels(self.novel_url)
		return self.obj.saveNovel(lang2=lang2)
	
	
	@addAttribute
	def saveSeries(self, lang2=""):
		print("开始下载系列小说……")
		if not isinstance(self.obj, PixivSeries):
			self.obj = PixivSeries(self.series_url)
		return self.obj.saveSeries(lang2=lang2)
	
	
	@addAttribute
	def saveSeriesAsZip(self, lang2=""):
		print("开始下载系列小说zip合集……")
		if not (self.obj, PixivSeries):
			self.obj = PixivSeries(self.series_url)
		return self.obj.saveAsZip(lang2=lang2)
	
	
	@addAttribute
	def saveSeriesAsTxt(self, lang2=""):
		print("开始下载系列小说txt合集……")
		if not isinstance(self.obj, PixivSeries):
			self.obj = PixivSeries(self.series_url)
		return self.obj.saveAsTxt(lang2=lang2)
	
	
	@addAttribute
	def saveAuthor(self, lang2=""):  # author
		print("开始下载此作者的全部小说……")
		if not isinstance(self.obj, PixivAuthor):
			self.obj = PixivAuthor(self.author_url)
		return self.obj.saveAuthor(lang2=lang2)
	
	
	@addAttribute
	def saveAuthorNovels(self, lang2=""):
		return self.saveAuthor(lang2=lang2)
	
	
	@addAttribute
	def saveAuthorIllusts(self):
		pass
	
	
	@addAttribute
	def saveAsZip(self, lang2=""):
		path = ""
		if isinstance(self.obj, PixivSeries):
			path = self.obj.saveAsZip(lang2=lang2)
		elif isinstance(self.obj, PixivAuthor):
			path = self.obj.saveAuthor(lang2=lang2)
		elif isinstance(self.obj, PixivIllusts):
			path = self.obj.saveAsZip()
		else:
			raise ValueError(f"{self.obj.__class__.__name__} 类中没有 {self.__class__.saveAsTxt.__name__} 方法")
		return path
	
	
	@addAttribute
	def saveAsTxt(self, lang2=""):
		path = ""
		if isinstance(self.obj, PixivNovels):
			path = self.obj.saveNovel(lang2=lang2)
		elif isinstance(self.obj, PixivSeries):
			path = self.obj.saveAsTxt(lang2=lang2)
		elif isinstance(self.obj, PixivFakeSeries):
			path = self.obj.saveAsTxt(lang2=lang2)
		# elif isinstance(self.obj, PixivAuthor):
		# 	path = self.obj.saveAuthorNovels(lang2=lang2)
		else:
			raise ValueError(f"{self.obj.__class__.__name__} 类中没有 {self.__class__.saveAsTxt.__name__} 方法")
		return path
	
	
def main():
	path, lang = "", ""
	lang = getLangSystem()
	string = input("\n请输入 Pixiv 或 Linpx 或 兽人控小说站 的小说链接或作者链接，按 Enter 键确认：\n")
	while string:
		if ("pixiv" in string or "furrynovel" in string) and re.search("\\d", string):
			try:
				url = getUrl(string)
				if re.search("zip", string, re.IGNORECASE):
					path = PixivObject(url).saveAsZip(lang)[0]
				elif re.search("txt", string, re.IGNORECASE):
					path = PixivObject(url).saveAsTxt(lang)[0]
				else:
					path = PixivObject(url).save(lang)[0]
			except ValueError as e:
				print(e)
			except RuntimeError as e:
				print(e)
				return
		else:
			print("输入有误，请重新输入，退出下载请直接按 Enter 键")
		string = input("\n请输入 Pixiv 或 Linpx 或 兽人控小说站 的小说链接或作者链接，按 Enter 键确认：\n")
		
	if os.path.isfile(path):
		path = os.path.dirname(path)
	openFile(path)
	print("已退出下载")


def test():  # tokenPoolInit() 不开线程才可用
	print(f"测试 {datetime.now()}\n")
	# a0 = PixivNovels(18012577).save()    #莱当社畜不如变胶龙  无系列
	# a1 = PixivNovels(17463359).save("zh_tw")    #莱恩的委托:双龙警察故事  无系列
	# a2 = PixivNovels(18131976).save("zh_cn")    # Summer Time is Naked Time 无系列
	# a3 = PixivNovels(15789643).save()   # 狼铠侠的末路，委托系列
	# a4 = PixivNovels(14059797).save()   # 浅色的蓝天，非委托系列，已删除
	# a5 = PixivNovels(18078490).save()   # 仅好P友可见
	# a6 = PixivNovels(15688116).save()   # 逗号分隔标签
	# a7 = PixivNovels(18004759).save()   # 斜杠分割标签
	
	# b0 = PixivSeries(2399683).save("zh_tw")  # 维卡斯委托系列
	# b0 = PixivSeries(2399683).setTelegramUploadInfo() # 维卡斯委托系列
	# b1 = PixivSeries(30656).save("zh_cn")    # 從今天起叫我主人 系列
	# b2 = PixivSeries(969137)  # 龙仆 委托系列
	# b2.getTokenTimes()
	# b2.save()
	# b3 = PixivSeries(PixivNovels(13929135).series_id)  # 隐藏部分章节
	# b3 = PixivSeries(1416918)  # 隐藏部分章节
	# b3.getNovelsList()
	# b3.save()
	
	# c0 = PixivAuthor(21129266).save("zh_tw")  # 维卡斯，有系列
	# c1 = PixivAuthor(16721009).save()   # 唐尼瑞姆，只有系列
	# c2 = PixivAuthor(13523138).save()   # 斯兹卡，没有系列
	# c3 = PixivAuthor(12261974)   # 龙仆，小说过多可能无法下载全部
	# c3 = PixivAuthor(38256034)   # 恩格里斯，小说过多可能无法下载全部
	# c3.getTokenTimes()
	# c3.save()
	
	# e = PixivIllusts(84943010)
	# print(e.info)
	# print(e.author_name)
	# print(e.series_name)
	# PixivIllusts(84943010).save()
	
	# fake_list = ['16901772', '16901870', '16902051', '16903146', '16903249', '16903329', '16903419', '16903493', '16903594', '16903670', '16903789', '16903859', '16903932', '16904019', '16904093', '16904224', '16904250', '16904295', '16904369']
	# fake_list = [
	# 	"https://www.pixiv.net/novel/show.php?id=15948620",
	# 	"https://www.pixiv.net/novel/series/7789216",
	# ]
	# f1 = PixivFakeSeries(fake_list)
	# f1 = PixivFakeSeries("\n".join(fake_list))
	# print(f1.__repr__())
	# f1.saveAsTxt()
	# f1.saveAsZip()
	# f1.save()
	
	# d0 = PixivObject("https://www.pixiv.net/novel/show.php?id=15789643").saveNovel()
	# d0 = PixivObject("https://www.pixiv.net/novel/show.php?id=15789643").saveSeries()
	# d0 = PixivObject("https://www.pixiv.net/novel/show.php?id=15789643").saveSeriesAsZip()
	# d0 = PixivObject("https://www.pixiv.net/novel/show.php?id=15789643").saveSeriesAsTxt()
	# d0 = PixivObject("https://www.pixiv.net/novel/show.php?id=15789643").saveAuthor("zh-tw")
	
	# d1 = PixivObject("https://www.pixiv.net/novel/series/8590168").saveSeries()
	# d1 = PixivObject("https://www.pixiv.net/novel/series/8590168").saveSeriesAsZip()
	# d1 = PixivObject("https://www.pixiv.net/novel/series/8590168").saveSeriesAsTxt()
	# d1 = PixivObject("https://www.pixiv.net/novel/series/8590168").saveNovel()
	# d1 = PixivObject("https://www.pixiv.net/novel/series/8590168").saveAuthor()
	# d1 = PixivObject("https://www.pixiv.net/novel/show.php?id=18762548").saveSeries() # 不死与不死，超长长篇
	
	# d2 = PixivObject("https://www.pixiv.net/users/10894035").saveAuthor()
	# d2 = PixivObject("https://www.pixiv.net/users/10894035").saveNovel()
	# d2 = PixivObject("https://www.pixiv.net/users/10894035").saveSeries()
	# d2 = PixivObject("https://www.pixiv.net/users/38256034")
	# d2.getTokenTimes()
	
	# d3 = PixivObject("https://www.pixiv.net/artworks/103646563").save()  #todo 暂不可用
	# d3 = PixivObject("https://www.pixiv.net/novel/show.php?id=19318723").save()
	# d3 = PixivObject("https://www.pixiv.net/novel/series/8590168").save()
	# d3 = PixivObject("https://www.pixiv.net/users/10894035").save()
	
	# d4 = PixivObject("https://furrynovel.ink/pixiv/novel/21954460").save()
	# d4 = PixivObject("https://furrynovel.com/zh/novel/6").save()  # Pixiv 系列有原文
	# d4 = PixivObject("https://furrynovel.com/zh/novel/8247").save()  # Pixiv 单篇有原文
	# d4 = PixivObject("https://furrynovel.com/zh/novel/501").save()  # bilibili 小说 ，Pixiv 无原文
	# d4 = PixivObject("https://furrynovel.com/zh/novel/827").save()  # 源网站已撤稿，Pixiv 单篇有原文
	
	
	
if True:
	tokenPoolInit()
	
	
if __name__ == "__main__":
	testMode = 1
	if testMode:
		test()
	else:
		main()
