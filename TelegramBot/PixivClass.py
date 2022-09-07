#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import math
import logging
from abc import ABC, abstractmethod
from functools import wraps
from ssl import SSLError

import numpy as np

from FileOperate import saveText, zipFile, openFile, timer
from PrintInfo import getFormattedTags, getInfoFromText, getFurryScore
from TextFormat import formatNovelName, formatCaption, formatText
from TokenRoundRobin import TokenRoundRobin
from Translate import getLanguage, getLangSystem, translate, transWords, transDir
from config import Pixiv_Tokens, default_path, testMode


sys.dont_write_bytecode = True
_TEST_WRITE = False
addTranslatedTags = 0   # 加入翻译过后的标签
tokenPool = TokenRoundRobin(Pixiv_Tokens)


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
			os._exit(1)
		except ValueError:
			logging.warning('None Value')
			# os._exit(1)
		except AttributeError as e:  # 'NoneType' object has no attribute 'title'
			logging.critical(f"AttributeError:{e}")
			logging.critical("网络/代理/Refresh Tokens 不可用；或请求频率过高")
			os._exit(1)
		except TypeError as e:  # 'NoneType' object is not callable
			logging.critical(f"TypeError: {e}")
			logging.critical("网络/代理/Refresh Tokens 不可用；或请求频率过高2")
			os._exit(1)
		except KeyboardInterrupt as e:
			logging.debug(e)
		except Exception as e:
			logging.error(e)
			os._exit(1)
	return wrapper


def getId(string: [int, str]) -> int:
	if re.search("\\d{5,}", str(string)):
		return int(re.search("\\d{5,}", str(string)).group())
	
		
class PixivABC(ABC):
	novel_id = 0       # 小说 ID
	novel_url = ""     # 小说网址
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
	author_name = ""   # 作者名字
	author_url = ""
	
	series_id = 0      # (所属)系列的 ID
	series_name = ""   # 系列名字
	series_url = ""
	count = 0          # 系列内篇数
	
	
	@abstractmethod    # 所有子类必须实现的方法
	def getJson(self):
		pass
	
	@abstractmethod
	def getInfo(self):
		pass
	
	@abstractmethod
	def __str__(self):
		pass
	
	def setFileInfo(self):
		pass
	
	def setLinkInfo(self):
		pass
	
	def getNovelsList(self):
		pass
	
	def getText(self):
		pass
	
	@abstractmethod
	def getLang(self):
		pass
	
	@abstractmethod
	def save(self):
		pass
	
	def setUploadInfo(self):
		pass
	
	def getScore(self):
		pass
	
	def getTokenTimes(self):
		pass
	
	
class PixivBase(PixivABC):  # 共用方法
	views = 0      # 点击数
	bookmarks = 0  # 收藏数
	comments = 0   # 评论数
	rate = 0       # 收藏率
	score = -100   # 推荐指数
	
	original_text = ""
	text = ""         # 小说文本
	lang = ""         # 小说语言
	furry_score = 0   # 兽人指数
	
	info = ""           # __str__()
	file_info = ""      # 写入文件的格式化信息
	link_info = ""      # 发送链接的格式化信息
	upload_info = ""    # 上传文件的格式化信息
	trans_upload_info = ""
	
	file_text = ""      # 小说文件文本
	file_path = ""      # 小说文件路径
	trans_path = ""     # 翻译文件路径
	trans_text = ""     # 翻译文件文本
	
	tags = set[str]()
	tags30 = set[str]()
	trans_tags = set[str]()
	telegram_info = ""  # 发送 Telegram 的信息
	
	
	@staticmethod
	def getTags(tagslist: list) -> set[str]:  # 处理 json.novel.tags
		tags = set()
		for tag in tagslist:
			tags.add(tag.name)
			if tag.translated_name and addTranslatedTags:
				tags.add(tag.translated_name)
		return tags
	
	# @checkNone
	@staticmethod
	def formatTags(tags: set) -> str:
		tags = list(tags)
		if tags:
			if "#" in tags[0]:
				tags = " ".join(tags)  # 有#直接间断
			else:
				tags = f"#{' #'.join(tags)}"  # 无#逐个添加
		else:
			tags = ""
		return tags
	
	
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
		return self.score
	
	
	def getFurryScore(self) -> int:
		self.furry_score = getFurryScore(self.file_text, self.tags)
		logging.info(f"【{self.title}】福瑞指数：{self.furry_score:.1f}")
		return self.furry_score
	
	
	def __str__(self) -> str:
		return f"未实现：{self.__class__.__name__}.__str__()"
	
	
	def __repr__(self) -> str:
		return self.__str__()
	
	
	def setFileInfo(self) -> str:  # 写入文件的信息
		if not self.lang:
			self.lang = getLanguage(self.title + self.caption)
		
		author = transWords("author", self.lang) + f"{self.author_name}\n"
		url = transWords("url", self.lang) + f"{self.novel_url}\n"
		tags = self.formatTags(self.tags)
		tags = transWords("hashtags", self.lang) + f"{tags}\n"
		if self.caption:
			self.caption = transWords("others", self.lang) + f"{self.caption}\n"
		
		if self.count > 0:
			print(f"【{self.title}】，共有{self.count}章")
		self.file_info = f"{self.title}\n{author}{url}{tags}{self.caption}"
		# logging.info(f"\n{self.file_info}")
		# print(self.file_info)
		return self.file_info
	
	
	def setLinkInfo(self) -> str:   # 发送链接后的文本
		info = f"未实现：{self.__class__.__name__}.setTelegramInfo()"
		return info
	
	
	@timer
	def setUploadInfo(self, lang2="") -> tuple[str, str]:  # 上传文件至 Telegram 的信息
		info2 = ""
		info1 = getInfoFromText(self.file_text, self.tags, self.lang)
		
		if lang2 and self.trans_text:
			info2 = getInfoFromText(self.trans_text, self.trans_tags, lang2)
		if __name__ == "__main__":
			print(info1, info2, sep="\n\n")
		return info1, info2
	
	
class PixivNovels(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	
	novel_id = 0
	original_text = ""  # 未格式化文本
	text = ""           # 已格式化文本
	
	file_path = ""      # 小说文件路径
	file_text = ""      # 小说文件文本
	trans_path = ""     # 翻译文件路径
	trans_text = ""     # 翻译文件文本
	trans_tags = set[str]()
	
	
	def __init__(self, novel_id: [int, str]):
		self.novel_id = getId(novel_id)
		self.novel_url = f"https://www.pixiv.net/novel/show.php?id={self.novel_id}"
		self.json = self.getJson()
		if self.json is not None:
			self.getInfo()
	
	
	@checkNone
	def getJson(self, force_update=False):
		if self._is_json_retrieved and not force_update:
			return self._original_json
		self._is_json_retrieved = True
		
		self._original_json = tokenPool.getAPI().novel_detail(self.novel_id)
		# print(json)
		return self._original_json
	
	
	def getInfo(self) -> None:
		novel = self.json.novel
		self.title = formatNovelName(novel.title)
		self.tags = self.getTags(novel.tags)
		self.caption = formatCaption(novel.caption)
		self.date = f"{novel.create_date[0:10]} {novel.create_date[11:19]}"
		self.pages = novel.page_count
		self.characters = novel.text_length
		
		self.views = novel.total_view
		self.bookmarks = novel.total_bookmarks
		self.comments = novel.total_comments
		self.score = self.getScore()
		
		self.author_id = novel.user.id
		self.author_name = novel.user.name
		self.series_id = novel.series.id
		self.series_name = novel.series.title
	
	
	@checkNone
	def getText(self, force_update=False) -> str:
		if self.original_text and force_update:
			return self.original_text
		
		if self.json.novel.visible:
			json = tokenPool.getAPI().novel_text(self.novel_id)
			self.original_text = json.novel_text
		else:
			logging.warning(f"这篇小说 {self.novel_id} 无权限访问，无法下载")
			self.original_text = f"【permission denied】【无权限访问，请与作者联系】\n{self.novel_url}"
		return self.original_text
	
	
	def getLang(self, force_update=False) -> str:
		if self.lang and not force_update:
			return self.lang
		if not self.original_text:
			self.getText()
		
		self.lang = getLanguage(self.original_text)
		self.tags.add(self.lang)
		return self.lang
	
	
	def __str__(self) -> str:
		tags = self.formatTags(self.tags)
		self.info = f"{self.title} By {self.author_name}\n" \
			f"阅读：{self.views}；收藏：{self.bookmarks}；评论：{self.comments}；" \
			f"推荐指数：{self.score}；福瑞指数：{self.furry_score}\n标签：{tags}\n" \
			f"{self.novel_url}\n"
		return self.info
	
	
	def setLinkInfo(self) -> str:
		tags = self.formatTags(self.tags)
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
	
	
	@timer
	def saveNovels(self, author="", series="", i=0, lang="", lang2="") -> tuple[str, str]:
		if not self.original_text:
			self.getText()
		if lang:
			self.lang = lang
		else:
			self.getLang()
		
		if author and series and i:  # 优化 SaveAuthor 调用 SaveAsZip & 单篇下载
			self.file_path = os.path.join(default_path, author, series, f"{i:0>2d} {self.title}.txt")
		elif series and i:  # 优化 SaveAsZip
			self.file_path = os.path.join(default_path, series, f"{i:0>2d} {self.title}.txt")
		else:   # 优化 SaveNovels
			self.file_path = os.path.join(default_path, f"{self.title}.txt")
		print(self.file_path)
		
		self.text = formatText(self.original_text, self.lang)
		self.file_info = self.setFileInfo()
		self.file_text = f"{self.file_info}\n\n{self.text}"
		saveText(self.file_path, self.file_text)
		
		if lang2 and self.lang != lang2:
			self.trans_tags = self.tags.copy()
			self.trans_tags.discard(self.lang)
			self.trans_tags.update([lang2, "translated"])
			# print(self.tags, self.trans_tags, sep="\n")
			
			part_path = self.file_path.replace(f"{default_path}\\", "")
			part_path = translate(part_path, lang1=self.lang, lang2=lang2)
			self.trans_path = os.path.join(default_path, transDir(lang2), part_path)
			self.trans_text = translate(self.file_text, lang1=self.lang, lang2=lang2, mode=1)
			saveText(self.trans_path, self.trans_text)
			print(self.trans_path)
		
		if not author and not series:  # 直接运行时
			info1, info2 = self.setUploadInfo(lang2)
			return (self.file_path, info1), (self.trans_path, info2)
		else:
			return self.file_path, self.trans_path
	
	
	def save(self, lang2="") -> tuple[str, str]:
		if self.series_id and __name__ == "__main__":
			print("当前小说存在系列，开始下载该系列")
			paths = PixivSeries(self.series_id).saveSeries(lang2=lang2)
		else:
			paths = self.saveNovels(lang2=lang2)
			self.getFurryScore()
		return paths
	
	
	def getTokenTimes(self) -> int:
		a = 0       # 初始化
		b = 1       # getInfo
		c = 1 + b   # getText
		print(a, b, c)
		return c


class PixivSeries(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	
	series_id = 0        # 系列的 ID
	series_name = ""     # 系列名字
	commission = ""      # 默认非委托系列
	count = 0            # 系列内的小说篇数
	characters = 0       # 系列字数
	
	novels_list = list[int]()      # 系列所有小说的 ID
	novels_names = list[str]()     # 系列所有小说名称
	novels_captions = list[str]()  # 系列所有小说名称
	tags = set[str]()    # 系列所有小说的 tags
	tags30 = set[str]()  # 系列前30小说的 tags
	
	novel_id = 0    # 系列第1篇小说的 ID
	novel_url = ""  # 系列第1篇小说的网址
	lang = ""       # 系列(第1篇)小说的语言
	info = ""       # __str__()
	text = ""       # 系列文本
	
	file_path = ""      # 系列文件（夹）路径
	file_text = ""      # 系列小说文本
	trans_path = ""     # 翻译文件路径
	trans_text = ""     # 翻译文件文本
	trans_tags = set[str]()
	
	
	def __init__(self, series_id: [int, str]):
		self.series_id = getId(series_id)
		self.series_uri = f"https://www.pixiv.net/novel/series/{self.series_id}"
		self.json = self.getJson()  # 原始数据
		if self.json is not None:
			self.getInfo()
	
	
	@checkNone
	def getJson(self, force_update=False) -> any:
		if self._is_json_retrieved and not force_update:
			return self._original_json
		self._is_json_retrieved = True
		
		self._original_json = tokenPool.getAPI().novel_series(self.series_id, last_order=None)
		return self._original_json
	
	
	def getInfo(self) -> None:
		series = self.json.novel_series_detail
		self.title = formatNovelName(series.title)  # 系列标题
		self.series_name = self.title
		self.caption = formatCaption(series.caption)  # 系列简介
		self.count = series.content_count  # 系列内小说数
		self.characters = series.total_character_count # 系列总字数
		self.author_id = series.user.id
		self.author_name = series.user.name
		
		novel = self.json.novel_series_first_novel   # 系列第1篇小说
		self.novel_id = novel.id
		self.novel_url = f"https://www.pixiv.net/novel/show.php?id={self.novel_id}"
		self.views = novel.total_view
		self.bookmarks = novel.total_bookmarks
		self.comments = novel.total_comments
		self.score = self.getScore()
		self.getTags30()
	
	
	def getTags30(self) -> None:
		self.tags30 = set()
		for novel in self.json.novels:
			self.tags30.update(self.getTags(novel.tags))
	
	
	def __str__(self) -> str:
		if not self.tags:
			self.tags = self.tags30
			
		tags = self.formatTags(self.tags)
		self.info = f"{self.title}  By {self.author_name}\n{tags}\n{self.series_uri}\n{self.novel_url}"
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
				self.novels_list.append(novel.id)
				if novel.visible:  # todo：如何处理无权限的小说？
					self.novels_list_part.append(novel.id)
					self.novels_names.append(novel.title)
					self.novels_captions.append(novel.caption)
					self.tags.update(self.getTags(novel.tags))
		
		self.tags = set() ; self.novels_list_part = []
		self.novels_list, self.novels_names, self.novels_captions = [], [], []
		addList(self.getJson())
		if len(self.novels_list) >= 30:  # 1次最多可请求到30个id
			next_qs = tokenPool.getAPI().parse_qs(self.json.next_url)
			while next_qs is not None:
				json = tokenPool.getAPI().novel_series(**next_qs)
				addList(json)
				next_qs = tokenPool.getAPI().parse_qs(json.next_url)
		
		count = len(self.novels_list_part)
		if self.count > count:
			logging.warning(f"有 {self.count - count} 篇小说，无权限下载")
			
		# print(len(self.novels_list), len(self.tags))
		# print(self.novels_list, self.novels_names, self.novels_captions, self.tags, sep="\n")
	
	
	def getLang(self, force_update=False) -> str:
		if self.lang and not force_update:
			return self.lang
		if not self.novels_list:
			self.getNovelsList()
		
		for novel_id in self.novels_list:
			self.lang = PixivNovels(novel_id).getLang()
			if self.lang:
				# print(self.lang)
				break
				
		self.tags.add(self.lang)
		return self.lang
	
	
	def checkCommission(self) -> bool:
		if not self.novels_list:
			self.getNovelsList()
		
		text = []  # 计算委托出现次数
		text.extend(self.novels_names)
		text.extend(self.novels_captions)
		text = " ".join(text)
		times = text.count("委托") + self.caption.count("委托")
		
		if times >= 0.2 * len(self.novels_list):
			self.commission = True
		else:
			self.commission = False
		return self.commission
	
	
	@timer
	def saveAsZip(self, author="", lang="", lang2="") -> tuple[str, str]:
		if not self.novels_list:
			self.getNovelsList()
		if lang:
			self.lang = lang
		else:
			self.getLang()
		
		path1, path2 = "", ""
		print(f"SaveAsZip: {self.title}")
		for i in range(len(self.novels_list)):
			novel = PixivNovels(self.novels_list[i])
			(path1, path2) = novel.saveNovels(author, self.title, i+1, self.lang, lang2)
		self.file_path = os.path.dirname(path1)
		print(self.file_path)
		
		if lang2 and self.lang != lang2:
			self.trans_path = os.path.dirname(path2)
			self.trans_tags = self.tags.copy()
			self.trans_tags.discard(self.lang)
			self.trans_tags.update([lang2, "translated"])
			# print(self.tags, self.trans_tags, sep="\n")
			
		if not author:  # 直接运行时
			self.file_path = zipFile(self.file_path)
			if self.trans_path:  # 压缩翻译目录
				self.trans_path = zipFile(self.trans_path, dir=transDir(lang2))
			info1, info2 = self.setUploadInfoForZip(lang2)
			return (self.file_path, info1), (self.trans_path, info2)
		else:
			return self.file_path, self.trans_path
	
	
	@timer
	def saveAsTxt(self, author="", lang="", lang2="") -> tuple[str, str]:
		if not self.novels_list:
			self.getNovelsList()
		
		if author:  # SaveAuthor 优化
			self.file_path = os.path.join(default_path, author, f"{self.title}.txt")
		else:       # SaveAsTxt 优化
			self.file_path = os.path.join(default_path, f"{self.title}.txt")
		print(f"SaveAsTxt: {self.title}")
		
		text = ""
		for i in range(len(self.novels_list)):
			novel_id = self.novels_list[i]
			novel = PixivNovels(novel_id)
			novel_title = novel.title
			novel_caption = novel.caption
			novel_text = novel.getText()
			
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
		self.file_info = self.setFileInfo()
		self.file_text = f"{self.file_info}\n\n{self.text}"
		saveText(self.file_path, self.file_text)
		print(self.file_path)
		
		if lang2 and self.lang != lang2:
			self.trans_tags = self.tags.copy()
			self.trans_tags.discard(self.lang)
			self.trans_tags.update([lang2, "translated"])
			# print(self.tags, self.trans_tags, sep="\n")
			
			part_path = self.file_path.replace(f"{default_path}\\", "")
			part_path = translate(part_path, lang1=self.lang, lang2=lang2)
			self.trans_path = os.path.join(default_path, transDir(lang2), part_path)
			self.trans_text = translate(self.file_text, lang1=self.lang, lang2=lang2, mode=1)
			saveText(self.trans_path, self.trans_text)
			print(self.trans_path)
		
		if not author:  # 直接运行时
			info1, info2 = self.setUploadInfo(lang2)
			return (self.file_path, info1), (self.trans_path, info2)
		else:
			return self.file_path, self.trans_path
	
	
	@timer
	def setUploadInfoForZip(self, lang2="") -> tuple[str, str]:  # 上传文件至 Telegram 的信息
		info2 = ""
		tags = getFormattedTags(self.tags)
		info1 = f"{self.title}\nBy #{self.author_name}\n{tags}\n{self.novel_url}"
		
		if lang2 and self.trans_path:
			title = os.path.splitext(os.path.basename(self.trans_path))[0]
			tags = getFormattedTags(self.trans_tags)
			info2 = f"{title}\nBy #{self.author_name}\n{tags}\n{self.novel_url}"
		# print(info1, info2, sep="\n\n")
		return info1, info2
	
	
	@timer
	def saveSeries(self, author="", lang="", lang2="") -> tuple[str, str]:
		if self.checkCommission():
			print("委托系列将下载成zip文件")
			paths = self.saveAsZip(author, lang, lang2)
			# self.getFurryScore()  # 无意义
		else:
			print("长篇小说将下载成txt文件")
			paths = self.saveAsTxt(author, lang, lang2)
			self.getFurryScore()
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


class PixivAuthor(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	
	webpage = ""     # 主页链接
	twitter = ""     # 推特链接
	followers = 0    # 总关注者
	
	manga = 0
	illusts = 0
	illusts_series = 0
	novels = 0
	novels_series = 0
	
	novels_list_all = list[int]()   # 全部小说 ID
	novels_list = list[int]()       # 无系列小说 ID
	series_list = list[int]()       # 全部系列 ID
	tags = set[str]()    # 所有小说的 tags
	lang = ""        # (最近1篇)小说语言
	
	author_dir = ""  # 文件夹路径
	file_path = ""   # 文件路径
	trans_path = ""  # 翻译文件路径
	
	
	def __init__(self, author_id: [int, str]):
		self.author_id = getId(author_id)
		self.author_url = f"https://www.pixiv.net/users/{self.author_id}"
		self.json = self.getJson()
		if self.json is not None:
			self.getInfo()
	
	
	@checkNone
	def getJson(self, force_update=False) -> any:
		if self._is_json_retrieved and not force_update:
			return self._original_json
		self._is_json_retrieved = True
		self._original_json = tokenPool.getAPI().user_detail(self.author_id)
		# print(json)
		return self._original_json
	
	
	def getInfo(self) -> None:
		user = self.json.user
		self.author_name = formatNovelName(user.name)
		self.author_dir = os.path.join(default_path, self.author_name)
		self.author_account = user.author_account
		self.profile_url = user.profile_image_urls.medium  # Profile pic
		self.caption = formatCaption(user.comment)
		
		profile = self.json.profile
		illusts = profile.total_illusts
		manga = profile.total_manga
		self.illusts = illusts + manga
		self.illusts_series = profile.total_illust_series
		self.novels = profile.total_novels
		self.novels_series = profile.total_novel_series
		
		self.webpage = profile.webpage
		self.twitter = profile.twitter_url
		self.followers = profile.total_follow_users
	
	
	def __str__(self) -> str:
		novels, nseries, illusts, iseries = self.novels, self.novels_series, self.illusts, self.illusts_series
		s = f"#{self.author_name} ({self.author_id})\n{self.author_url}\n"
		if self.webpage:
			s += f"主页：{self.webpage}\n"
		if self.twitter:
			s += f"推特：{self.twitter}\n"
		
		if novels and self.novels_list:
			snovel = len(self.novels_list)
			s += f"小说：{novels}篇：单篇：{snovel}篇；系列：{nseries}个共{novels - snovel}篇\n"
		elif novels:
			s += f"小说：{novels}篇：系列：{nseries}个\n"
			
		if illusts:
			s += f"插画：{illusts}幅；系列：{iseries}个\n"
		self.info = s.strip()
		# print(self.info)
		return self.info

	
	def setLinkInfo(self) -> str:
		self.link_info = f"{self.author_name}\n"
		if self.novels >= 1:
			self.link_info += f"小说：{self.novels}篇，系列：{self.novels_series}个"
		if self.illusts >= 1:
			self.link_info += f"插画：{self.illusts}幅，系列：{self.illusts_series}个"
		# print(self.link_info)
		return self.link_info.strip()
		
	
	def getNovelsList(self, force_update=False) -> None:
		if (self.novels_list or self.series_list) and not force_update:
			return
		
		def addList(json: any):
			for novel in json.novels:
				self.novels_list_all.append(novel.id)
				if not novel.series.id:
					self.novels_list.append(novel.id)
				elif novel.series.id not in self.series_list:
					self.series_list.append(novel.series.id)
				self.tags.update(self.getTags(novel.tags))
						
		self.tags = set()
		self.novels_list_all, self.novels_list, self.series_list = [], [], []
		json = tokenPool.getAPI().user_novels(self.author_id)
		addList(json)
		next_qs = tokenPool.getAPI().parse_qs(json.next_url)
		while next_qs is not None:
			json = tokenPool.getAPI().user_novels(**next_qs)
			addList(json)
			next_qs = tokenPool.getAPI().parse_qs(json.next_url)
		
		# print(len(self.novels_list_all), len(self.novels_list), len(self.series_list), sep="\n")
		# print(self.novels_list_all, self.novels_list, self.series_list, self.tags, sep="\n")
	
	
	def getLang(self, force_update=False) -> str:
		if self.lang and not force_update:
			return self.lang
		if not self.novels_list_all:
			self.getNovelsList()
		
		for novel_id in self.novels_list_all:  # 避免第1篇无法获取语言
			self.lang = PixivNovels(novel_id).getLang()
			if self.lang:
				# print(self.lang)
				break
				
		self.tags.add(self.lang)
		return self.lang
	
	
	def setAuthorDir(self) -> None:
		self.author_dir = os.path.join(default_path, self.author_name)
		if not os.path.exists(self.author_dir):
			os.makedirs(self.author_dir)
	
	
	def saveAuthorIcon(self, force_update=False) -> str:
		if not os.path.exists(self.author_dir):
			self.setAuthorDir()
			
		name = f"{self.author_name}.jpg"
		path = os.path.join(self.author_dir, name)
		if os.path.exists(path) and force_update:
			os.remove(path)
		elif os.path.exists(path):
			print(path)
			return path
		else:
			try:
				tokenPool.getAPI().download(self.profile_url, path=self.author_dir, name=name)
			except Exception as e:
				logging.error(e)  # 代理需支持UDP
			else:
				print(path)
				return path
	
	
	def saveAuthorInfo(self) -> str:
		if not os.path.exists(self.author_dir):
			self.setAuthorDir()
		if not self.lang:
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
		print(path)
		return path
	
		
	@timer
	def saveAuthorNovels(self, lang2="") -> tuple[tuple[str, str], tuple[str, str]]:
		if not os.path.exists(self.author_dir):
			self.setAuthorDir()
		if not self.novels_list:
			self.getNovelsList()
		if not self.lang:
			self.getLang()
		
		path1, path2 = "", ""
		single = transWords("single", self.lang)
		for i in range(len(self.novels_list)):
			novels = PixivNovels(self.novels_list[i])
			path1, path2 = novels.saveNovels(self.author_name, single, i+1, self.lang, lang2)
		for j in range(len(self.series_list)):
			series = PixivSeries(self.series_list[j])
			path1, path2 = series.saveSeries(self.author_name, self.lang, lang2)
		print(222, self.author_dir)
		self.file_path = zipFile(self.author_dir)
		
		if lang2 and self.lang != lang2:
			path2 = path2.replace(f"{default_path}\\", "")
			path2 = path2.split("\\")[:2]
			path2 = "\\".join(path2)
			path2 = os.path.join(default_path, path2)
			print(222, path2)
			self.trans_path = zipFile(path2, dir=transDir(lang2))
			
		info1, info2 = self.setUploadInfo(lang2)
		return (self.file_path, info1), (self.trans_path, info2)
	
	
	@timer
	def setUploadInfo(self, lang2="") -> tuple[str, str]:  # 上传文件至 Telegram 的信息
		info2 = ""
		info1 = f"#{self.author_name} #ID{self.author_id} #{self.lang}\n"
		singel = len(self.novels_list)
		if self.novels_list:
			info1 += f"小说：{self.novels}篇：单篇：{singel}篇\n"
		if self.novels_series:
			info1 += f"系列：{self.novels_series}个，共{self.novels - singel}篇\n"
		info1 += f"{self.author_url}"
			
		if lang2:
			info2 = translate(info1, lang2=lang2, lang1=self.lang)
			info2 = info2.replace(f"#{self.lang}", f"#{lang2}")
		if __name__ == "__main__":
			print(info1, info2, sep="\n\n")
		return info1, info2
	
	
	@timer
	def saveAuthor(self, lang2="") -> tuple:
		self.setAuthorDir()
		self.getNovelsList()
		self.getLang()
		self.saveAuthorIcon()
		self.saveAuthorInfo()
		paths = self.saveAuthorNovels(lang2=lang2)
		self.getTokenTimes()
		return paths
	
	
	def save(self, lang2="") -> tuple:
		return self.saveAuthor(lang2=lang2)
	
	
	def getNovelsData(self) -> list[list]:
		if not self.novels_list:
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
			if not self.novels_list:
				self.getNovelsList()
			
			num = 2 * len(self.novels_list) + b
			for i in range(len(self.series_list)):
				num += PixivSeries(self.series_list[i]).getTokenTimes()
			print(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name} 预估下载请求次数为：{num}")
		else:
			print(f"{self.__class__.__name__}.{sys._getframe().f_code.co_name} 略估下载请求次数为：{num}")
			
		if num >= 390:
			print(f"请求过多({num}次)，可能无法完全下载")
		return num
		

# @checkNone
def main():
	path = ""
	language = getLangSystem()
	string = input("\n请输入Pixiv或Linpx小说链接或作者链接，按 Enter 键确认：\n")
	
	while string != "":
		if ("pixiv" in string or "/pn/" in string) and re.search("[0-9]{5,}", string):
			id = getId(string)
			if "novel/series" in string:
				print("开始下载系列小说……")
				path = PixivSeries(id).save(language)[0][0]
			elif "novel" in string:    # 去末尾s，兼容linpx
				print("开始下载单章小说……")
				path = PixivNovels(id).save(language)[0][0]
			elif "user" in string:     # 去末尾s，兼容linpx
				print("开始下载此作者的全部小说……")
				path = PixivAuthor(id).save(language)[0][0]
			elif "artworks" in string:
				print("不支持下载插画，请重新输入")
				# PixivIllust(id).save()   # todo
			else:
				print("输入有误，请重新输入")
		else:
			print("输入有误，请重新输入，退出下载请直接按 Enter 键")
		string = input("\n请输入Pixiv或Linpx小说链接或作者链接，按 Enter 键确认：\n")
		
	if os.path.isfile(path):
		path = os.path.dirname(path)
	openFile(path)
	print("已退出下载")


def test():
	print("测试\n")
	# a0 = PixivNovels(18012577).save()    #莱当社畜不如变胶龙  无系列
	# a1 = PixivNovels(17463359).save("zh_tw")    #莱恩的委托:双龙警察故事  无系列
	# a2 = PixivNovels(18131976).save("zh_cn")    # Summer Time is Naked Time 无系列
	# a3 = PixivNovels(15789643).save()   # 狼铠侠的末路，委托系列
	# a4 = PixivNovels(14059797).save()   # 浅色的蓝天，非委托系列
	
	# b0 = PixivSeries(2399683).save("zh_tw")  # 维卡斯委托系列
	# b0 = PixivSeries(2399683).setTelegramUploadInfo() # 维卡斯委托系列
	# b1 = PixivSeries(30656).save("zh_cn")    # 從今天起叫我主人 系列
	# b1 = PixivSeries(30656)    # 從今天起叫我主人 系列
	# b1.save("zh_cn")
	# b1.setUploadInfo()
	# b1.setUploadInfoForTrans()  # 從今天起叫我主人 系列
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
	# c3.getTokenTimes()
	# c3.save()


if __name__ == "__main__":
	testMode = 0
	if testMode:
		test()
	else:
		main()
		
