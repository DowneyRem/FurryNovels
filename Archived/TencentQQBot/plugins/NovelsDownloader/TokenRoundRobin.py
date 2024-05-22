#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import logging
from threading import Thread

import pixivpy3
from pixivpy3 import AppPixivAPI, ByPassSniApi

from .configuration import Pixiv_Tokens, proxy_list, testMode


class TokenRoundRobin:
	apis = []
	tokenCount = 0       # token 可用数目
	callCount = 0        # token 累计调用次数
	runCount = 0         # token 更新次数
	duration = 10 * 60   # token 更新间隔时间，秒
	expiration = 0       # token 本次过期时间
	expiration_last = 0  # token 上次过期时间
	if testMode:
		duration = 10
	
	
	def __init__(self, tokens: list = Pixiv_Tokens):
		print(f"当前 Pixiv tokens 更新时间为：{self.duration} 秒")
		self.expiration = time.time()  # 初始化过期时间，第一次直接登录
		self.update(tokens)            # 直接使用 update 避免同时登录两次
		# self.updateTokens(tokens)
		# self.checkTokens(tokens)
		# self.check(tokens)
	
		
	def checkTokens(self, tokens: list = Pixiv_Tokens):
		self.runCount += 1
		self.tokenCount = 0
		REQUESTS_KWARGS = {'proxies': {'https': proxy_list[0]}, }
		for i in range(len(tokens)):
			token = tokens[i]
			if not isinstance(token, str):
				continue
				
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
		logging.info(f"{self.runCount}. Finished initialising, {self.tokenCount} tokens is available.")
		self.expiration = time.time() + self.duration
		
		if self.tokenCount == 0:
			logging.critical("请检查网络，或更换 Pixiv Tokens")
			raise RuntimeError("请检查网络，或更换 Pixiv Tokens")
		
	
	def updateTokens(self, tokens: list):
		while True:
			while time.time() >= self.expiration:
				self.expiration_last = self.expiration
				self.checkTokens(tokens)
				# print(f"运行时间：{self.expiration - self.expiration_last}\n")
				time.sleep(self.duration)  # 减少阻塞 todo 如何解决？
				# [base_events.py:1891]  Executing <Task finished name='Task-21' coro=<Command.run() done, defined at C:\Program Files\Python310\lib\site-packages\nonebot\command\__init__.py:106> result=True created at C:\Program Files\Python310\lib\asyncio\tasks.py:636> took 3.172 seconds
				
				
	
	def check(self, tokens=Pixiv_Tokens):
		t1 = Thread(target=TokenRoundRobin.checkTokens, args=(self, tokens))
		t1.daemon = True
		t1.start()
		# t1.join()   # 会阻塞 TelegramBot 启动
	
	
	def update(self, tokens=Pixiv_Tokens):
		t2 = Thread(target=TokenRoundRobin.updateTokens, args=(self, tokens))
		t2.daemon = True
		t2.start()
	
	
	def getAPI(self) -> AppPixivAPI:
		self.callCount += 1
		if self.tokenCount >= 1:
			logging.info(f"Requesting token #{(self.callCount-1) % self.tokenCount +1}, total {self.callCount}")
			return self.apis[self.callCount % self.tokenCount]
	