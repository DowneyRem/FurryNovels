#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging

from FileOperate import timer
from TokenRoundRobin import TokenRoundRobin
from configuration import addTranslatedTags


# testMode = 0
# tokenPool = TokenRoundRobin()
def tokenPoolInit():
	global tokenPool
	try:
		tokenPool = TokenRoundRobin()
	except RuntimeError as e:
		print(e)
		logging.critical(f"{e}")
		return
	

class Base(object):
	@staticmethod
	# @timer
	def input(*words):
		if len(words) == 1:  # 传入tuple，内部只有1参数，拆成list；有多个直接for循环
			words = words[0].split(" ")
		
		s = set()
		for word in words:
			if word.startswith("#") or word.startswith("＃"):  # 去#号方能搜索
				word = word[1:]
			s.add(word)
		keyword = " ".join(s).replace("　", "")  # 去全角空格
		print(f"{words=}\n{keyword=}")
		
		if keyword == "":
			raise ValueError("搜索内容不能为空")
		return keyword
	
	
	@staticmethod
	def getTags(tagslist: list) -> set[str]:  # 处理 json.novel.tags
		tags = set()
		for tag in tagslist:
			if "R-18" in tag.name:  # R18,R18G 规范化
				tags.add(tag.name.replace("-", ""))
			else:
				tags.add(tag.name)
				
			if tag.translated_name and addTranslatedTags:
				tags.add(tag.translated_name)
		# print(tags)
		return tags
	
		
	@staticmethod
	def getNovels(json):
		result = {}
		for novel in json.novels:
			info = {
				"id": novel.id,
				"url": f"https://www.pixiv.net/novel/show.php?id={novel.id}",
				"title": novel.title,
				"author": novel.user.name,
				"author_id": novel.user.id,
				"series": novel.series.name,
				"series_id": novel.series.id,
				"tags": Base.getTags(novel.tags),
			}
			if testMode:
				print(info)
			result[novel.id] = info
		# print(result)
		return result
	
	
	@staticmethod
	def getIllusts(json):
		result = {}
		for illust in json.illusts:
			info = {
				"id": illust.id,
				"url": f"https://www.pixiv.net/artworks/{illust.id}",
				"title": illust.title,
				"author": illust.user.name,
				"author_id": illust.user.id,
				"tags": Base.getTags(illust.tags),
				"download_url": illust.image_urls.large,
			}
			if testMode:
				print(info)
			result[illust.id] = info
		# print(result)
		return result
		
		
	@staticmethod
	def getUsers(json):
		result = {}
		for user in json.user_previews:
			# print(user.user)
			user = user.user
			info = {
				"id": user.id,
				"url": f"https://www.pixiv.net/users/{user.id}",
				"name": user.name,
				"account": user.account,
				"icon": user.profile_image_urls.medium,
			}
			if testMode:
				print(info)
			result[user.id] = info
		# print(result)
		return result
	
	
class Users(object):
	"""
	优先返回完全匹配的内容，没有则返回全部搜索结果
	"""
	
	@staticmethod
	def Keyword(*words):
		keyword = Base.input(*words)
		json = tokenPool.getAPI().search_user(keyword)
		return Base.getUsers(json)
	
	
class Novels(object):
	"""
	# _SEARCH_TARGET: TypeAlias = Literal[
	# "partial_match_for_tags", "exact_match_for_tags", "title_and_caption", "keyword", ""
	# 部分标签，完全标签 匹配标题和描述 关键词
	# 部分标签 完全标签 正文 标签和标题和说明文字
	"""
	
	@staticmethod
	def PartialTags(*words):
		keyword = Base.input(*words)
		json = tokenPool.getAPI().search_novel(keyword, search_target="partial_match_for_tags")
		return Base.getNovels(json)
	
	
	@staticmethod
	def ExactTags(*words):
		keyword = Base.input(*words)
		json = tokenPool.getAPI().search_novel(keyword, search_target="exact_match_for_tags")
		return Base.getNovels(json)
	
	
	@staticmethod
	def TitleCaption(*words):
		keyword = Base.input(*words)
		json = tokenPool.getAPI().search_novel(keyword, search_target="title_and_caption")
		return Base.getNovels(json)
	
	
	@staticmethod
	# @timer
	def Keyword(*words):
		keyword = Base.input(*words)
		json = tokenPool.getAPI().search_novel(keyword, search_target="keyword")
		return Base.getNovels(json)
	
	
class Illusts(object):
	"""
	# _SEARCH_TARGET: TypeAlias = Literal[
	# "partial_match_for_tags", "exact_match_for_tags", "title_and_caption", ""
	# 部分标签，完全标签 匹配标题和描述
	# 部分标签 完全标签 正文
	"""
	
	@staticmethod
	def PartialTags(*words):
		keyword = Base.input(*words)
		json = tokenPool.getAPI().search_illust(keyword, search_target="partial_match_for_tags")
		return Base.getIllusts(json)
	
	
	@staticmethod
	def ExactTags(*words):
		keyword = Base.input(*words)
		json = tokenPool.getAPI().search_illust(keyword, search_target="exact_match_for_tags")
		return Base.getIllusts(json)
	
	
	@staticmethod
	def TitleCaption(*words):
		keyword = Base.input(*words)
		json = tokenPool.getAPI().search_illust(keyword, search_target="title_and_caption")
		return Base.getIllusts(json)
	
	
	@staticmethod
	def Keyword(*words):
		# return Illusts.TitleCaption(*words)
		return Illusts.PartialTags(*words)
	
	
class PixivSearch(object):
	Users = Users
	Novels = Novels
	Illusts = Illusts
	
	
# 重命名
PixivSearchUsers = Users
PixivSearchNovels = Novels
PixivSearchIllusts = Illusts
	
	
def test():
	print("test")
	# tokenPoolInit()
	# Users.Keyword("唐尼")
	# Novels.Keyword("唐尼")
	# Illusts.Keyword("唐尼")
	# PixivSearch.Novels.Keyword("#龍", "#furry", "#R-18")
	# PixivSearch.Novels.Keyword("龍", "furry", "R-18")
	# PixivSearch.Novels.Keyword("#龍 #furry #R-18")
	# PixivSearch.Novels.Keyword("龍 furry R-18")
	# PixivSearch.Novels.Keyword(" 　")  # 空内容报错
	
	
if True:
	tokenPoolInit()


if __name__ == '__main__':
	testMode = 1
	if testMode:
		test()
