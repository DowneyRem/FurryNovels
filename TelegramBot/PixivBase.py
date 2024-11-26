#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import math
import logging
from abc import ABC, abstractmethod

import numpy as np

from GetLanguage import getLanguage
from PrintInfo import getFormattedTags, getInfoFromText
from Translate import translate, transWords, transPath
from configuration import addTranslatedTags


sys.dont_write_bytecode = True
_TEST_WRITE = False


class PixivABC(ABC):
	link = ""  # 传入链接
	novel_id = 0  # 小说 ID
	novel_url = ""  # 小说网址
	novel_name = ""
	
	illust_id = 0  # 插画 ID
	illust_url = ""  # 插画网址
	illust_name = ""
	medium_urls = []  # 压缩链接
	original_urls = []  # 原图链接
	
	title = ""  # 标题
	tags = set[str]()  # tags
	caption = ""  # Caption
	text = ""  # 小说文本
	date = ""  # 创建日期
	pages = 0  # 页面数
	characters = 0  # 字数
	
	views = 0  # 点击数
	bookmarks = 0  # 收藏数
	comments = 0  # 评论数
	
	author_id = 0  # 作者 ID
	author_url = ""
	author_name = ""  # 作者名字
	author_icon = ""
	
	series_id = 0  # (所属)系列的 ID
	series_url = ""
	series_name = ""  # 系列名字
	count = 0  # 系列内篇数
	
	
	@abstractmethod  # 所有子类必须实现的方法
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
	views = 0  # 点击数
	bookmarks = 0  # 收藏数
	comments = 0  # 评论数
	rate = 0  # 收藏率
	score = -100  # 推荐指数
	commission = None              # 默认非委托系列
	
	novels_list_all = list[int]()  # 所有小说的 ID
	novels_list = list[int]()  # 所有可见小说的 ID
	novels_names = list[str]()  # 所有可见小说名称
	novels_captions = list[str]()  # 系列所有可见小说 capithon
	single_list = list[int]()  # 无系列小说 ID
	series_list = list[int]()  # 全部系列 ID
	lang = ""  # 小说语言
	
	title = ""  # 标题
	author_name = ""  # 作者名字
	novel_url = ""  # 小说网址
	tags = set[str]()  # tags
	caption = ""  # Caption
	info = ""  # __str__()
	link_info = ""  # 发送链接后的信息 setLinkInfo()
	file_head = ""  # 小说文件头部信息 setFileHead()
	
	file_path = ""  # 小说文件路径
	file_text = ""  # 小说文件文本
	# tags = set[str]()  # tags
	file_info = ""  # 下载后，上传Telegram的信息 setFileInfo()
	furry = 0
	
	trans_path = ""  # 翻译文件路径
	trans_text = ""  # 翻译文件文本
	trans_tags = set[str]()
	trans_info = ""  # 上传Telegram的翻译信息
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
			self.novels_names.append(novel.title)
			self.novels_captions.append(novel.caption)
	
	
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
			nums = [];
			a = -7.75;
			step1 = 1;
			step2 = 0.75
			for a in np.arange(a, a + 9 * step1, step1):  # 生成首列数据
				b = np.arange(a, a + 21 * step2, step2)  # 生成首行数据
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
		if not self.novels_list:
			self.getNovelsList()
		
		text = []
		text.extend(self.novels_names)
		text.extend(self.novels_captions)
		self.lang = getLanguage("".join(text))
		self.tags.add(self.lang)
		return self.lang
	
	
	def __repr__(self) -> str:
		return f"{self.__class__.__name__}('{self.link}')"
	
	
	def setLinkInfo(self) -> str:  # 发送链接后的文本
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
	
	
	def checkCommission(self) -> bool:
		if self.commission is not None:
			return self.commission
		
		if not self.novels_list:
			self.getNovelsList()
		text = []  # 计算委托出现次数
		text.extend([self.title, self.caption])
		text.extend(self.novels_names)
		text.extend(self.novels_captions)
		text = " ".join(str(i) for i in text)
		times = text.count("委托") + text.count("约稿") + text.count("約稿") + text.count("commission")
		
		if times >= 0.2 * len(self.novels_list):
			self.commission = True
			self.tags.add("Commission")
		else:
			self.commission = False
			self.tags.add("Series")
		return self.commission
	
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
	
	
	def checkLanguage(self):
		if "zh" in self.file_info and "zh_cn" in self.file_info:
			pass
		if "zh" in self.file_info and "zh_tw" in self.file_info:
			pass
		if "zh_cn" in self.file_info and "zh_tw" in self.file_info:
			pass


class PixivNovelBase(PixivBase):
	pass


class PixivSeriesBase(PixivBase):
	pass

