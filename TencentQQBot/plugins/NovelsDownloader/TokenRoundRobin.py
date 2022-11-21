#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import pixivpy3
from pixivpy3 import AppPixivAPI, ByPassSniApi

from .configuration import Pixiv_Tokens, proxy_list


class TokenRoundRobin:
	apis = []
	tokenCount = 0
	callCount = 0


	def __init__(self, tokens: list = Pixiv_Tokens):
		REQUESTS_KWARGS = {'proxies': {'https': proxy_list[0]}, }
		for i in range(len(tokens)):
			token = tokens[i]
			if not isinstance(token, str):
				continue
				
			try:
				api = AppPixivAPI(**REQUESTS_KWARGS)
				api.set_accept_language("en-us")  # zh-cn
				api.auth(refresh_token=token)
				print(f"{token} is OK!")
				self.apis.append(api)
				self.tokenCount += 1
				
			# except pixivpy3.utils.PixivError as e:
			# 	print("尝试使用 BAPI")
			# 	api = ByPassSniApi()
			# 	api.require_appapi_hosts()
				
			except pixivpy3.utils.PixivError as e:
				# print(f"请检查网络是否可用，或更换TOKEN{i+1} ")
				print(f"{i + 1}. {token} is not OK, ignoring!")
		print(f"Finished initialising, {self.tokenCount} tokens is available.")
		
		if self.tokenCount == 0:
			# logging.critical("请检查网络，或更换 Pixiv Tokens")
			raise RuntimeError("请检查网络，或更换 Pixiv Tokens")


	def getAPI(self) -> AppPixivAPI:
		self.callCount += 1
		if self.tokenCount >= 1:
			logging.info(f"Requesting token #{(self.callCount-1) % self.tokenCount +1}, total {self.callCount}")
			return self.apis[self.callCount % self.tokenCount]
	