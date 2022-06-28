#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import pixivpy3
from pixivpy3 import AppPixivAPI
from platform import platform


logging.basicConfig(level=logging.INFO,
		format='%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
		datefmt='%Y.%m.%d. %H:%M:%S',
		# filename='parser_result.log',
		# filemode='w'
		)


class TokenRoundRobin:
	aapis = []
	tokenCount = 0
	callCount = 0

	def __init__(self, tokens: list):
		if "Windows" in platform():
			REQUESTS_KWARGS = {'proxies': {'https': 'http://127.0.0.1:10808', }}
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
				print("{} is not OK, ignoring!".format(t))
		print("Finished initialising, {} tokens is available.".format(self.tokenCount))

	def getAAPI(self) -> AppPixivAPI:
		self.callCount += 1
		logging.info(f"Requesting token, returning #{self.callCount % self.tokenCount}, total {self.callCount}")
		return self.aapis[self.callCount % self.tokenCount]
