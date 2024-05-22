#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import logging


# 测试模式，执行test而非main
testMode = 0
print(f"{testMode=}")


# 设置默认目录
folder = os.path.dirname(__file__)
novel_folder = os.path.join(folder, "Novels")
illust_folder = os.path.join(folder, "Illusts")
trans_folder = os.path.join(folder, "Translation")
down_folder = os.path.join(folder, "downInfo")


def monthNow() -> str:
	year, month = str(time.localtime()[0]), str(time.localtime()[1])
	if len(month) == 1:
		month = f"0{month}"
	return os.path.join(year, month)


# 是否再路径中加入时间
setTimeInDefaultPath = 1
if setTimeInDefaultPath:  # Linux
	novel_path = os.path.join(novel_folder, monthNow())
	illust_path = os.path.join(illust_folder, monthNow())


# 项目代理设置
# proxy_list 中应只保留一项，否则以第一项为准
proxy_list = [
	"",  # 不使用代理
	# 'http://127.0.0.1:1080',
	# 'http://127.0.0.1:7890',
	# 'http://127.0.0.1:10808',
	]


# logging 全局配置
logging.basicConfig(
		# level=logging.DEBUG,
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
	"0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4",
	]
    

# 加入翻译过后的标签
addTranslatedTags = 0


# Telegram & Heroku 配置
# 你的 Telegram Bot Token
# 获取方式 @BotFather
if testMode:
	BOT_TOKEN = ""
else:
	BOT_TOKEN = ""
	
	
WEB_HOOK = f""
TEST_CHANNEL = ""


# Webdav 配置
# 默认加密列表
encryptlist = [
	"https://dav.jianguoyun.com/dav/",
	]


# Webdav4 配置
webdavdict4 = {
	"jianguoyun": {
		"baseurl": "",
		"username": "",  # 你的账号，支持多组
		"password": ""   # 你的密码
	},
}


# 公用内容
# Translate 与 fomatText 共用语言列表
cjklist = "zh zh_cn zh_tw zh_hk zh-hans zh-hant ja ko".split(" ")
eulist = "en fr de ru pt es".split()
