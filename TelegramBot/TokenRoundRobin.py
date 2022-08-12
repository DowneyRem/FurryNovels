#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
from platform import platform

import pixivpy3
from pixivpy3 import AppPixivAPI

from config import proxy_windows


logging.basicConfig(level=logging.INFO,
		format='%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
		datefmt='%Y.%m.%d. %H:%M:%S',
		# filename='parser_result.log',
		# filemode='w'
		)


# todo：代理设置循环，区分代理问题与token问题
# requests_kwargs_windows = [
# 	{'proxies': {'https': 'http://127.0.0.1:1080', }},
# 	{'proxies': {'https': 'http://127.0.0.1:7890', }},
# 	{'proxies': {'https': 'http://127.0.0.1:10808', }},
# 	]
# requests_kwargs_linux = []


class TokenRoundRobin:
	aapis = []
	tokenCount = 0
	callCount = 0

	def __init__(self, tokens: list):
		if "Windows" in platform():
			# REQUESTS_KWARGS = {'proxies': {'https': 'http://127.0.0.1:10808', }}
			REQUESTS_KWARGS = {'proxies': {'https': proxy_windows[0]}, }
		elif "Linux" in platform():
			REQUESTS_KWARGS = {}
			
		for i in range(len(tokens)):
			t = tokens[i]
			if not isinstance(t, str):
				continue
			try:
				aapi = AppPixivAPI(**REQUESTS_KWARGS)
				aapi.set_accept_language("en-us")  # zh-cn
				aapi.auth(refresh_token=t)
				print("{} is OK!".format(t))
				self.aapis.append(aapi)
				self.tokenCount += 1
				
			except pixivpy3.utils.PixivError as e:
				print(f"请检查网络可用性，或更换TOKEN{i+1} ")
				print(f"{t} is not OK, ignoring!")
		print(f"Finished initialising, {self.tokenCount} tokens is available.")

	def getAAPI(self) -> AppPixivAPI:
		self.callCount += 1
		if self.tokenCount == 0:
			logging.critical("请检查网络可用性，或更换TOKENS")
			os._exit(1)
		else:
			logging.info(f"Requesting token #{(self.callCount-1) % self.tokenCount +1}, total {self.callCount}")
			return self.aapis[self.callCount % self.tokenCount]

