# !/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import os
import json
import shutil
import logging
import requests
from typing import Any, Dict, Optional
from functools import wraps

from PixivBase import PixivBase
# from PixivClass import PixivNovels, PixivSeries, PixivAuthor
from FileOperate import saveText, zipFile, openFile, removeFile, timer
from FurryNovelWeb import getOriginalLink, getUrl, getId
from GetLanguage import getLanguage, getLangSystem
# from PrintInfo import getFormattedTags, getInfoFromText
from TextFormat import formatNovelName, formatCaption, formatText
from Translate import translate, transWords, transPath
from configuration import novel_folder, OUTPUT_LINPX_LINK


class JsonDict(dict):  # type: ignore[type-arg]
	"""general json object that allows attributes to be bound to and also behaves like a dict"""
	
	def __getattr__(self, attr: Any) -> Any:
		return self.get(attr)
	
	def __setattr__(self, attr: Any, value: Any) -> None:
		self[attr] = value


class LinpxApi(object):
	ParsedJson = Any
	LINPX_HEADERS = {"referer": "https://furrynovel.ink/"}
	
	
	@classmethod
	def parse_json(cls, json_str: str | bytes) -> ParsedJson:
		"""parse str into JsonDict"""
		return json.loads(json_str, object_hook=JsonDict)
	
	
	@classmethod
	def requests_call(cls, url) -> ParsedJson:
		response = requests.request(method="GET", url=url, headers=LinpxApi.LINPX_HEADERS)
		# print(url)
		return LinpxApi.parse_json(response.text)
	
	
	@classmethod
	def getNovel(cls, novel_id: [int, str]) -> ParsedJson:
		return LinpxApi.requests_call(f"https://api.furrynovel.ink/pixiv/novel/{novel_id}/cache")
	
	
	@classmethod
	def getNovels(cls, novel_ids: [list[int, str]]) -> ParsedJson:
		url_part = "&ids[]=".join(str(i) for i in novel_ids)
		return LinpxApi.requests_call(f"https://api.furrynovel.ink/pixiv/novels/cache?ids[]={url_part}")
	
	
	@classmethod
	def getSeries(cls, series_id: [int, str]) -> ParsedJson:
		return LinpxApi.requests_call(f"https://api.furrynovel.ink/pixiv/series/{series_id}/cache")
	
	
	@classmethod
	def getAuthor(cls, author_id: [int, str]) -> ParsedJson:
		return LinpxApi.requests_call(f"https://api.furrynovel.ink/pixiv/user/{author_id}/cache")
	
	
	@classmethod
	def getAuthors(cls, author_ids: [list[int, str]]) -> ParsedJson:
		url_part = "&ids[]=".join(str(i) for i in author_ids)
		return LinpxApi.requests_call(f"https://api.furrynovel.ink/pixiv/users/cache?ids[]={url_part}")
	
	
	@classmethod
	def downloadPic(cls, url, file, headers):
		with requests.request(method="GET", url=url, headers=headers, stream=True) as response:
			if isinstance(file, str):
				with open(file, "wb") as out_file:
					shutil.copyfileobj(response.raw, out_file)
			else:
				shutil.copyfileobj(response.raw, file)  # type: ignore[arg-type]
		return file
		
		
	@classmethod
	def downloadPixivImage(cls, pxImgUrl, file) -> str:
		url = f"https://pximg.furrynovel.ink/?url={pxImgUrl}&w=800"
		return LinpxApi.downloadPic(url, file, headers=LinpxApi.LINPX_HEADERS)
	
	
	@classmethod  # 使用 pixiv.cat 获取插图，非 Linpx
	def downloadPixivIllust(cls, illust_id, order, file) -> str:
		url = f"https://pixiv.re/{illust_id}-{order}.png"
		# url = f"https://pixiv.nl/{illust_id}-{order}.png"
		return LinpxApi.downloadPic(url, file, headers={})
	
	
# class LinpxNovels(PixivNovels):
class LinpxNovels(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	original_text = ""  # 未格式化文本
	
	
	def __init__(self, link: [int, str]):
		self.link = link
		self.novel_id = getId(link)
		if OUTPUT_LINPX_LINK:
			self.novel_url = f"https://furrynovel.ink/pixiv/novel/{self.novel_id}/cache"
		else:
			self.novel_url = f"https://www.pixiv.net/novel/show.php?id={self.novel_id}"
		self.json = self.getJson()
		self.checkJson()
	
	
	def getJson(self, force_update=False):
		if self._is_json_retrieved and not force_update:
			return self._original_json
		
		self._original_json = LinpxApi.getNovel(self.novel_id)
		self._is_json_retrieved = True
		# print(self._original_json)
		return self._original_json
	
	
	def checkJson(self):
		if not self.json:
			raise RuntimeError("网络状态不佳，请稍后再次尝试")
		if self.json.error:
			raise ValueError(f"Linpx 上不存在该小说{self.novel_id}")
		else:  # 正常小说
			self.getInfo()
	
	
	def getInfo(self) -> None:
		novel = self.json
		self.title = self.novel_name = formatNovelName(novel.title)
		self.author_id = novel.userId
		self.author_name = novel.userName
		self.author_url = f"https://www.pixiv.net/users/{self.author_id}"
		
		self.tags = set(novel.tags)
		self.caption = formatCaption(novel.desc)
		self.date = f"{novel.createDate[0:10]} {novel.createDate[11:19]}"
		self.characters = len(self.text)
		
		self.views = novel.pixivReadCount
		self.bookmarks = novel.pixivLikeCount
		self.comments = 0
		self.score = self.getScore()
		
		if novel.series:
			self.series_id = novel.series.id
			self.series_url = f"https://www.pixiv.net/novel/series/{self.series_id}"
			self.series_name = novel.series.title
	

	def getText(self, force_update=False) -> str:
		self.original_text = self.json.content
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
		else:  # 优化 SaveNovel
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


# class LinpxSeries(PixivSeries):
class LinpxSeries(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	
	series_id = 0  # 系列的 ID
	series_url = ""
	series_name = ""  # 系列名字
	count = 0  # 系列内的小说篇数
	
	novels_list_all = list[int]()  # 系列所有小说的 ID
	novels_list = list[int]()      # 系列所有可见小说的 ID
	novels_names = list[str]()     # 系列所有可见小说名称
	novels_captions = list[str]()  # 系列所有可见小说 capithon
	commission = None  # 默认非委托系列
	lang = ""  # 系列语言
	
	tags = set[str]()  # 系列所有可见小说的 tags
	tags30 = set[str]()  # 系列前30小说的 tags
	
	novel_id = 0  # 系列第1篇小说的 ID
	novel_url = ""  # 系列第1篇小说的网址
	novel_name = ""  # 系列第1篇小说名称
	
	novels_json: any = None
	
	
	def __init__(self, link: [int, str]):
		self.link = link
		self.series_id = getId(link)
		self.series_url = f"https://www.pixiv.net/novel/series/{self.series_id}"
		self.json = self.getJson()  # 原始数据
		self.checkJson()
	
	
	def getJson(self, force_update=False):
		if self._is_json_retrieved and not force_update:
			return self._original_json
		
		self._original_json = LinpxApi.getSeries(self.series_id)
		self._is_json_retrieved = True
		# print(self._original_json)
		return self._original_json
	
	
	def checkJson(self):
		if not self.json:
			raise RuntimeError("网络状态不佳，请稍后再次尝试")
		if self.json.error:
			raise ValueError(f"Linpx 上不存在该小说{self.series_id}")
		else:  # 正常小说
			self.getInfo()
	
	
	def getInfo(self) -> None:
		series = self.json
		self.author_id = self.json.userId
		self.author_name = series.userName
		self.author_url = f"https://www.pixiv.net/users/{self.author_id}"
		
		self.title = self.series_name = formatNovelName(series.title)
		self.caption = formatCaption(series.caption)  # 系列简介
		self.count = series.total # 系列内小说数
		self.tags = set(series.tags)
		self.novel_id = series.novels[0].id
		if OUTPUT_LINPX_LINK:
			self.novel_url = f"https://furrynovel.ink/pixiv/novel/{self.novel_id}/cache"
		else:
			self.novel_url = f"https://www.pixiv.net/novel/show.php?id={self.novel_id}"
		self.novels_json = series.novels
		self.getNovelsList()
		
		
	def getNovelsList(self, force_update=False) -> None:
		if self.novels_list and self.tags and not force_update:
			return
		
		self.tags = set()   # 第二次下载时，清空原有内容
		self.novels_list, self.novels_names, self.novels_captions = [], [], []
		for novel in self.novels_json:
			self.novels_list.append(novel.id)
			self.novels_names.append(novel.title)
			self.novels_captions.append(novel.desc)
			self.tags.update(novel.tags)
		
		
	def __str__(self) -> str:
		tags = self.formatTags()
		self.info = f"{self.title}  By {self.author_name}\n{self.caption}\n{tags}\n{self.series_url}\n{self.novel_url}"
		return self.info


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
				novel = LinpxNovels(self.novels_list[i])
				# if isinstance(self, LinpxSeries):
				# 	novel = LinpxNovels(self.novels_list[i])
				#
				# else:
				# 	novel = PixivNovels(self.novels_list[i])
				(path1, path2) = novel.saveNovel(author, self.title, i + 1, self.lang, lang2)
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
		else:  # SaveAsTxt 优化
			self.file_path = os.path.join(novel_folder, f"{self.title}.txt")
		
		text = ""
		for i in range(len(self.novels_list)):
			novel_id = self.novels_list[i]
			try:
				novel = LinpxNovels(self.novels_list[i])
				# if isinstance(self, LinpxSeries):
				# 	novel = LinpxNovels(self.novels_list[i])
				# else:
				# 	novel = PixivNovels(self.novels_list[i])
				novel_title = novel.title
				novel_caption = novel.caption
				novel_text = novel.getText()
				self.tags.update(novel.tags)
		
			except ValueError as e:
				print(e)
				logging.error(e)
				novel_text = f"无法获取{novel_id}所在的章节"
			else:
				novel_title_replaced = novel_title.replace(self.title, "").replace("-", "")
				if len(novel_title_replaced) >= 2:
					novel_title = novel_title_replaced
				if ("第" not in novel_title) and ("章" not in novel_title):
					novel_title = f"第{i + 1}章 {novel_title}"
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


class LinpxFakeSeries(LinpxSeries):
	def __init__(self, links: [str, list]):  # 可处理小说网址或小说ID
		if isinstance(links, str) and "\n" in links:
			links = links.split()
		if isinstance(links, list):
			if "pixiv" in str(links[0]):
				self.links = links
			else:   # 数字id列表
				if OUTPUT_LINPX_LINK:
					self.links = [f"https://furrynovel.ink/pixiv/novel/{i}/cache" for i in links]
				else:
					self.links = [f"https://www.pixiv.net/novel/show.php?id={i}" for i in links]
				
			self.link = "\n".join(links)
			self.commission = False  # 默认下载成 TXT
			self.getNovelsList(force_update=True)  # 检测 Series 链接，并入 self.novels_list
			self.count = len(self.novels_list)
			self.getInfo()
	
	
	def getInfo(self):
		self.novel_id = self.novels_list[0]  # 系列第1篇小说
		self.novel = LinpxNovels(self.novel_id)
		self.novel_url = self.novel.novel_url
		self.novel_name = self.novel.novel_name
		self.title = self.series_name = re.sub(r"\d", "", self.novel_name)
		self.tags.update(self.novel.tags)
		self.caption = self.novel.caption
		self.characters += self.novel.characters
		
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
				series = LinpxSeries(link)
				series.getNovelsList(force_update=True)  # 强制更新
				self.novels_list.extend(series.novels_list)
			elif "novel" in link or "pn" in link:  # 去末尾s，兼容linpx
				self.novels_list.append(link)
	
	
	def __repr__(self) -> str:
		return f"{self.__class__.__name__}({self.links})"
	
	
	def saveAsTxt(self, author="", lang="", lang2="") -> tuple:
		return super().saveAsTxt(author, lang, lang2)


	def saveAsZip(self, author="", lang="", lang2="") -> tuple:
		return super().saveAsZip(author, lang, lang2)

	
	def setLinkInfo(self) -> str:
		return "将多个链接视为一个系列小说？"


class LinpxAuthor(PixivBase):
	_is_json_retrieved = False
	_original_json: any
	
	author_id = 0  # 作者 ID
	author_url = ""
	author_name = ""  # 作者名字
	profile_url = ""  # 头像链接
	caption = ""  # 作者简介
	webpage = ""  # 主页链接
	twitter = ""  # 推特链接
	followers = 0  # 总关注者
	
	manga = 0
	illusts_count = 0
	illusts_series_count = 0
	novels_count = 0
	novels_series_count = 0
	
	novels_list = list[int]()  # 所有可见小说 ID
	single_list = list[int]()  # 无系列小说 ID
	series_list = list[int]()  # 全部系列 ID
	novel_id = 0  # 最近1篇小说
	series_id = 0  # 最近1篇系列小说
	
	novels_names = list[str]()  # 所有小说名称
	novels_captions = list[str]()  # 所有小说 capithon
	novels_data = list[str, int]()
	lang = ""  # 小说语言
	
	series_json = None
	series_names = list[str]()
	series_captions = list[str]()
	
	author_dir = ""  # 文件夹路径
	file_path = ""  # 文件路径
	file_info = ""
	trans_path = ""  # 翻译文件路径
	trans_info = ""
	
	
	def __init__(self, link: [int, str]):
		self.link = link
		self.author_id = getId(link)
		self.author_url = f"https://www.pixiv.net/users/{self.author_id}"
		self.json = self.getJson()
		self.checkJson()
	
	
	def getJson(self, force_update=False):
		if self._is_json_retrieved and not force_update:
			return self._original_json
		
		self._original_json = LinpxApi.getAuthor(self.author_id)
		self._is_json_retrieved = True
		# print(self._original_json)
		return self._original_json
	
	def checkJson(self):
		if not self.json:
			raise RuntimeError("网络状态不佳，请稍后再次尝试")
		if self.json.error:
			raise ValueError(f"Linpx 上不存在该小说{self.series_id}")
		else:  # 正常小说
			self.getInfo()
			
			
	def getInfo(self) -> None:
		user = self.json
		self.title = self.author_name = formatNovelName(user.name)
		self.author_dir = os.path.join(novel_folder, self.author_name)
		self.profile_url = self.author_icon = user.imageUrl  # Profile pic
		self.caption = formatCaption(user.comment)
		# self.getNovelsList()
	
	
	def __str__(self) -> str:
		self.info = f"#{self.author_name} ({self.author_id})\n{self.author_url}\n"
		# if self.webpage:
		# 	self.info += f"主页：{self.webpage}\n"
		# if self.twitter:
		# 	self.info += f"推特：{self.twitter}\n"
		
		if self.novels_count and self.single_list:
			single_novels = len(self.single_list)
			self.info += f"小说：{self.novels_count}篇：单篇：{single_novels}篇;系列：{self.novels_series_count}个，共{self.novels_count - single_novels}篇\n"
		elif self.novels_count:
			self.info += f"小说：{self.novels_count}篇：系列：{self.novels_series_count}个\n"
		
		if self.illusts_count:
			self.info += f"插画：{self.illusts_count}幅；系列：{self.illusts_series_count}个\n"
		self.info = self.info.strip()
		# print(self.info)
		return self.info
	
	
	def getNovelsList(self, force_update=False) -> None:
		if (self.single_list or self.series_list) and not force_update:
			return
		
		self.tags = set()  # 第二次下载时，清空原有内容
		self.series_list, self.series_names, self.series_captions = [], [], []
		self.novels_list, self.novels_names, self.novels_captions = [], [], []
		self.single_list = []
		
		for series in self.json.series:
			self.series_list.append(series.id)
			self.series_names.append(series.title)
			self.series_captions.append(series.caption)
			self.tags.update(series.tags)
		
		self.novels_list = list(self.json.novels)
		self.novels_count = len(self.novels_list)
		self.novels_series_count = len(self.series_list)
		self.novel_id = self.novels_list[0]
		if OUTPUT_LINPX_LINK:
			self.novel_url = f"https://furrynovel.ink/pixiv/novel/{self.novel_id}/cache"
		else:
			self.novel_url = f"https://www.pixiv.net/novel/show.php?id={self.novel_id}"
		
		novels_detail = LinpxApi.getNovels(self.novels_list)
		for novel in novels_detail:
			self.novels_names.append(novel.title)
			self.novels_captions.append(novel.desc)
			self.tags.update(novel.tags)
			if not novel.seriesId:
				self.single_list.append(novel.id)
			# elif novel.seriesId not in self.series_list:
			# 	self.series_list.append(novel.seriesId)
		# print(self.series_list)
		# print(self.single_list)
	
	
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
				LinpxApi.downloadPixivImage(self.profile_url, path)
			except Exception as e:
				logging.error(e)
		
		if os.path.exists(path):
			print(f"作者头像：{path}")
		return path
	
	
	def saveAuthorInfo(self) -> str:
		self.makeAuthorDir()
		text = [self.author_name, self.author_url, self.caption]
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
				novels = LinpxNovels(self.single_list[i])
				path1, path2 = novels.saveNovel(self.author_name, single, i + 1, self.lang, lang2)
			except ValueError as e:
				print(e)
				logging.error(e)
		
		for j in range(len(self.series_list)):
			try:
				series = LinpxSeries(self.series_list[j])
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
			self.file_info += f"小说：{self.novels_count}篇：单篇：{single_novels}篇\n"
		if self.novels_series_count:
			self.file_info += f"系列：{self.novels_series_count}个，共{self.novels_count - single_novels}篇\n"
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
		# self.getNovelsList(force_update=True)  # 已在 PixivFactory 中强制更新
		self.getLang()
		self.saveAuthorIcon()
		self.saveAuthorInfo()
		paths = self.saveAuthorNovels(lang2=lang2)
		# self.getTokenTimes()
		return paths
	
	
	def save(self, lang2="") -> tuple:
		return self.saveAuthor(lang2=lang2)


class LinpxFactory(object):
	url = ""  # 传入的 url
	novel_url = ""  # 小说 url
	illust_url = ""
	series_url = ""  # 系列小说 url
	author_url = ""  # 作者 url
	lang = ""
	tags = set[str]()  # tags
	
	novel_id = 0
	illust_id = 0
	series_id = 0
	author_id = 0
	score = 0
	
	file_path = ""  # 小说文件路径
	file_info = ""  # 上传Telegram的信息
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
		self.obj = None  # 初始化变量，防止旧数据未被覆盖
		self.file_path, self.trans_path = "", ""
		self.file_info, self.trans_info = "", ""
		self.score, self.furry = 0, 0
		self.lang, self.tags = "", set()
		self.author_id, self.author_name = 0, ""
		self.novel_id, self.series_id = 0, 0
		if (isinstance(string, str) and "\n" in string) or isinstance(string, list):
			self.obj = LinpxFakeSeries(string)
		elif isinstance(string, str):
			self._url = getUrl(string)  # 用于保留 furrynovel.com 的网址链接
			self.url = self._url
			self.factory()
			# 不可创建线程 AttributeError: 'PixivFactory' object has no attribute 'obj'
			# t2 = Thread(target=PixivFactory.factory, args=(self,))
			# t2.start()
			# t2.join()  # 不join AttributeError: 'PixivFactory' object has no attribute 'obj'
		
		
	def factory(self):
		# url=f"https://furrynovel.ink/pixiv/user/{author_id}/cache"
		if "user" in self.url:  # 去末尾s，兼容linpx
			self.obj = LinpxAuthor(self.url)
		# self.obj.getNovelsList(force_update=True)  # 强制更新
		elif "user" in self.url and "series" in self.url:
			raise ValueError("输入链接有误，不支持漫画/插画系列")
		elif "series" in self.url:
			self.obj = LinpxSeries(self.url)
		# self.obj.getNovelsList(force_update=True)  # 强制更新
		elif "novel" in self.url or "pn" in self.url:  # 去末尾s，兼容linpx
			self.obj = LinpxNovels(self.url)
		# elif "artwork" in self.url:
		# 	self.obj = LinpxIllusts(self.url)
		# 	self.illust_id = self.obj.illust_id
		# 	self.illust_url = self.obj.illust_url
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
	
	@addAttribute
	def save(self, lang2=""):  # 默认下载
		print("开始下载……")
		return self.obj.save(lang2=lang2)
	
	
	@addAttribute
	def saveNovel(self, lang2=""):
		print("开始下载单章小说……")
		if not isinstance(self.obj, LinpxNovels):
			self.obj = LinpxNovels(self.novel_url)
		return self.obj.saveNovel(lang2=lang2)
	
	
	@addAttribute
	def saveSeries(self, lang2=""):
		print("开始下载系列小说……")
		if not isinstance(self.obj, LinpxSeries):
			self.obj = LinpxSeries(self.series_url)
		return self.obj.saveSeries(lang2=lang2)
	
	
	@addAttribute
	def saveSeriesAsZip(self, lang2=""):
		print("开始下载系列小说zip合集……")
		if not (self.obj, LinpxSeries):
			self.obj = LinpxSeries(self.series_url)
		return self.obj.saveAsZip(lang2=lang2)
	
	
	@addAttribute
	def saveSeriesAsTxt(self, lang2=""):
		print("开始下载系列小说txt合集……")
		if not isinstance(self.obj, LinpxSeries):
			self.obj = LinpxSeries(self.series_url)
		return self.obj.saveAsTxt(lang2=lang2)
	
	
	@addAttribute
	def saveAuthor(self, lang2=""):  # author
		print("开始下载此作者的全部小说……")
		if not isinstance(self.obj, LinpxAuthor):
			self.obj = LinpxAuthor(self.author_url)
		return self.obj.saveAuthor(lang2=lang2)


def test():
	print(f"测试\n{__file__}")
	
	# a0 = LinpxNovels(18012577).save()    #莱当社畜不如变胶龙  无系列
	# a1 = LinpxNovels(17463359).save("zh_tw")    #莱恩的委托:双龙警察故事  无系列
	# # a2 = LinpxNovels(18131976).save("zh_cn")    # Summer Time is Naked Time 无系列，Linpx 不存在
	# a3 = LinpxNovels(15789643).save()   # 狼铠侠的末路，委托系列
	# a4 = LinpxNovels(14059797).save()   # 浅色的蓝天，初遇,非委托系列，已删除
	# a5 = LinpxNovels(18078490).save()   # 胶龙少年在校运会2，仅好P友可见
	# a6 = LinpxNovels(15688116).save()   # 魔物化大陆：第一章-真心为你上，逗号分隔标签
	# a7 = LinpxNovels(18004759).save()   # 第三章 意外察觉到异常事态的帅哥学弟，斜杠分割标签
	
	# b0 = LinpxSeries(2399683)
	# print(b0.novel_id)
	# b0 = LinpxSeries(2399683).save("zh_tw")  # 维卡斯委托系列
	# b0 = LinpxSeries(2399683).setTelegramUploadInfo() # 维卡斯委托系列
	# b1 = LinpxSeries(30656).save("zh_cn")    # 從今天起叫我主人 系列
	# b2 = LinpxSeries(969137)  # 龙仆 委托系列
	# b2.save()
	# b3 = LinpxSeries(LinpxNovels(13929135).series_id)  # 隐藏部分章节
	# b3 = LinpxSeries(1416918)  # 隐藏部分章节
	# b3.getNovelsList()
	# b3.save()

	
	# c0 = LinpxAuthor(21129266).save("zh_tw")  # 维卡斯，有系列
	# c1 = LinpxAuthor(16721009).save()   # 唐尼瑞姆，只有系列
	# c2 = LinpxAuthor(13523138).save()   # 斯兹卡，没有系列
	# c3 = LinpxAuthor(12261974)   # 龙仆，小说过多可能无法下载全部
	# c3 = LinpxAuthor(38256034)   # 恩格里斯，小说过多可能无法下载全部
	# c3.getTokenTimes()
	# c3.save()
	
	# fake_list = ['16901772', '16901870', '16902051', '16903146', '16903249', '16903329', '16903419', '16903493', '16903594', '16903670', '16903789', '16903859', '16903932', '16904019', '16904093', '16904224', '16904250', '16904295', '16904369']
	# fake_list = [
	# 	"https://www.pixiv.net/novel/show.php?id=15948620",
	# 	"https://www.pixiv.net/novel/series/7789216",
	# ]
	# f1 = LinpxFakeSeries(fake_list)
	# f1 = LinpxFakeSeries("\n".join(fake_list))
	# print(f1.__repr__())
	# f1.saveAsTxt()
	# f1.saveAsZip()
	# f1.save()
	
	# d0 = LinpxFactory("https://www.pixiv.net/novel/show.php?id=15789643").saveNovel()
	# d0 = LinpxFactory("https://www.pixiv.net/novel/show.php?id=15789643").saveSeries()
	# d0 = LinpxFactory("https://www.pixiv.net/novel/show.php?id=15789643").saveSeriesAsZip()
	# d0 = LinpxFactory("https://www.pixiv.net/novel/show.php?id=15789643").saveSeriesAsTxt()
	# d0 = LinpxFactory("https://www.pixiv.net/novel/show.php?id=15789643").saveAuthor("zh-tw")
	
	# d1 = LinpxFactory("https://www.pixiv.net/novel/series/8590168").saveSeries()
	# d1 = LinpxFactory("https://www.pixiv.net/novel/series/8590168").saveSeriesAsZip()
	# d1 = LinpxFactory("https://www.pixiv.net/novel/series/8590168").saveSeriesAsTxt()
	# d1 = LinpxFactory("https://www.pixiv.net/novel/series/8590168").saveNovel()
	# d1 = LinpxFactory("https://www.pixiv.net/novel/series/8590168").saveAuthor()
	# d1 = LinpxFactory("https://www.pixiv.net/novel/show.php?id=18762548").saveSeries() # 不死与不死，超长长篇
	
	# d2 = LinpxFactory("https://www.pixiv.net/users/10894035").saveAuthor()
	# d2 = LinpxFactory("https://www.pixiv.net/users/10894035").saveNovel()
	# d2 = LinpxFactory("https://www.pixiv.net/users/10894035").saveSeries()
	# d2 = LinpxFactory("https://www.pixiv.net/users/38256034")
	# d2.getTokenTimes()
	
	# d3 = LinpxFactory("https://www.pixiv.net/artworks/103646563").save()  #todo 暂不可用
	# d3 = LinpxFactory("https://www.pixiv.net/novel/show.php?id=19318723").save()
	# d3 = LinpxFactory("https://www.pixiv.net/novel/series/8590168").save()
	# d3 = LinpxFactory("https://www.pixiv.net/users/10894035").save()
	
	
if __name__ == "__main__":
	test()
	