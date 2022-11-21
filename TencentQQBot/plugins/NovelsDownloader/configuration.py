#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import logging
from config import testMode # 测试模式
print(f"{testMode=}")


def monthNow() -> str:
	year, month = str(time.localtime()[0]), str(time.localtime()[1])
	if len(month) == 1:
		month = f"0{month}"
	return os.path.join(year, month)


# 设置默认目录
setTimeInDefaultPath = 1
if setTimeInDefaultPath:  # Linux
	novel_path = os.path.join(os.path.dirname(__file__), "Novels", monthNow())
else:
	novel_path = os.path.join(os.path.dirname(__file__), "Novels")
	
translation_path = os.path.join(os.path.dirname(__file__), "Translation")


# 项目代理设置
# proxy_list 中应只保留一项，否则以第一项为准
proxy_list = [
	"",  # 不使用代理
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


# Pixv 配置
# 你的 Pixiv REFRESH_TOKEN
# 获取方式如下，请替换后再使用
# https://github.com/upbit/pixivpy/issues/158#issuecomment-778919084
# https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362
Pixiv_Tokens = [
	"0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4",  # pypixiv官方
	]

if testMode:
	Pixiv_Tokens = [Pixiv_Tokens[0]]
	
	
# Pixiv WebAPI所用到的cookie
# 目前仅Recommend使用取该列表第一个
Pixiv_Cookie = [
	]

# Telegram & Heroku 配置
# 你的 Telegram Bot Token
# 获取方式 @BotFather
if testMode:
	BOT_TOKEN = ""
else:
	BOT_TOKEN = ""
heroku_app_name = ""
TEST_CHANNEL = ""


# 默认密码
password = "furry"


# Webdav 配置
# 强制加密列表
encryptlist = [
	"https://dav.jianguoyun.com/dav/",
	]


# Webdav4 配置
webdavdict4 = {
	"jianguoyun": {
		"baseurl": "https://dav.jianguoyun.com/dav/",
		"username": "",  # 你的账号，支持多组
		"password": ""   # 你的密码
	},
}


# Webdav3.py 配置
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


# 公用内容
# Translate 与 fomatText 共用语言列表
cjklist = "zh zh_cn zh_tw zh_hk zh-hans zh-hant ja ko".split(" ")
eulist = "en fr de ru pt es".split()
