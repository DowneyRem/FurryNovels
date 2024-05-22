#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import random
import logging

import pixivpy3
from pixivpy3 import AppPixivAPI, ByPassSniApi

from configuration import Pixiv_Tokens, proxy_list, testMode


class TokenRoundRobin:
	apis = []
	tokenCount = 0         # token 可用数目
	callCount = 0          # token 累计调用次数
	runCount = 0           # token 更新次数格式
	RunCountMax = 100      # 单一 Token 请求最大次数
	
	
	def __init__(self, tokens: list = Pixiv_Tokens):
		logging.info(f"初始化 Pixiv tokens")
		self.checkTokens(tokens)
	
	
	def login(self, token, i=0):
		# REQUESTS_KWARGS = {'proxies': {'https': proxy_list[0]}, }
		# REQUESTS_KWARGS = {'proxies': "http://127.0.0.1:7890", }  # 无需/不可指定代理
		REQUESTS_KWARGS = {'proxies': "", }
		try:
			api = AppPixivAPI(**REQUESTS_KWARGS)
			api.set_accept_language("en-us")  # zh-cn
			api.auth(refresh_token=token)
			self.apis.append(api)
			self.tokenCount += 1
			# print(f"{token} is OK!")
			logging.debug(f"{token} is OK!")
		except pixivpy3.utils.PixivError as e:
			logging.debug(f"{i + 1}. {token} is not OK, ignoring!")
	
	
	def checkTokens(self, tokens: list = Pixiv_Tokens):
		self.runCount += 1
		self.tokenCount = 0
		for i in range(len(tokens)):
			token = tokens[i]
			if isinstance(token, str):
				self.login(token, i)
		logging.info(f"{self.runCount}. Finished initialising, {self.tokenCount} tokens is available.")
		
		if self.tokenCount == 0:
			logging.critical("请检查网络，或更换 Pixiv Tokens")
			raise RuntimeError("请检查网络，或更换 Pixiv Tokens")
		
	
	def getAPI0(self) -> AppPixivAPI:
		self.callCount += 1
		if self.tokenCount >= 1:
			logging.info(f"Requesting token #{(self.callCount-1) % self.tokenCount +1}, total {self.callCount}")
			return self.apis[self.callCount % self.tokenCount]
	
	
	def getAPI(self) -> AppPixivAPI:
		self.callCount += 1
		if self.tokenCount >= 1:
			i = int((self.callCount / self.RunCountMax) % self.tokenCount)
			# print(f"{self.callCount=}，{self.tokenCount=}，{i=}，")
			logging.info(f"Requesting token #{i+1}, total {self.callCount}")
			# time.sleep(random.random())
			return self.apis[i]
	
	
if __name__ == "__main__":
	tokenPool = TokenRoundRobin()
	