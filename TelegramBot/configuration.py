#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import logging
from platform import platform


def monthNow() -> str:
	year, month = str(time.localtime()[0]), str(time.localtime()[1])
	if len(month) == 1:
		month = f"0{month}"
	return os.path.join(year, month)
	
	
# 设置默认目录
setTimeInDefaultPath = 1
if "Linux" in platform() or setTimeInDefaultPath:  # Linux
	novel_path = os.path.join(os.path.dirname(__file__), "Novels", monthNow())
else:
	novel_path = os.path.join(os.path.dirname(__file__), "Novels")
	
translation_path = os.path.join(os.path.dirname(__file__), "Translation")
# 测试模式，执行test而非main
testMode = 1


# 项目代理设置
# proxy_list 中应只保留一项，否则以第一项为准
proxy_list = [
	# 'http://127.0.0.1:1080',
	# 'http://127.0.0.1:7890',
	'http://127.0.0.1:10808',
	]
	

# logging 全局配置
logging.basicConfig(
		level=logging.INFO,
		format='%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
		datefmt='%Y.%m.%d. %H:%M:%S',
		# filename='parser_result.log',
		# filemode='w'
		)


# Pixv配置
# 你的 Pixiv REFRESH_TOKEN
# 获取方式如下，请替换后再使用
# https://github.com/upbit/pixivpy/issues/158#issuecomment-778919084
# https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362
Pixiv_Tokens = [
	"0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4",
	]


# Pixiv WebAPI所用到的cookie
# 目前仅Recommend使用取该列表第一个
Pixiv_Cookie = [
	]


# Telegram & Heroku 配置
# 你的 Telegram Bot Token
# 获取方式 @BotFather
BOT_TOKEN = ""
TEST_TOKEN = ""
heroku_app_name = ""
TEST_CHANNEL = ""


# Webdav 配置
# 默认加密列表
encryptlist = ["https://dav.jianguoyun.com/dav/",
               ]


# Webdav3 配置
webdavdict3 ={
	"jianguoyun": {
		'webdav_hostname': "https://dav.jianguoyun.com/dav/",
		'webdav_login': "",     # 你的账号，支持多组
		'webdav_password': "",  # 你的密码
		'disable_check': True,  # 有的网盘不支持check功能
		'proxy_hostname': "",   # 代理功能暂时无法使用
		'proxy_login': "",
		'proxy_password': "",
		'disable_check': True,
	},
}


# Webdav4 配置
webdavdict4 = {
	"jianguoyun": {
		"baseurl": "https://dav.jianguoyun.com/dav/",
		"username": "",  # 你的账号，支持多组
		"password": ""   # 你的密码
	},
}


# 公用内容
# Translate 与 fomatText 共用语言列表
cjklist = "zh zh_cn zh_tw zh_hk ja ko".split(" ")
eulist = "en fr de ru pt es ".split()
