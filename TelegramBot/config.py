#!/usr/bin/python
# -*- coding: UTF-8 -*-
from opencc import OpenCC
cc1 = OpenCC('tw2sp.json')  # 繁转简
cc2 = OpenCC('s2twp.json')  # 簡轉繁


# Pixv配置
# 你的 Pixiv REFRESH_TOKEN
# 获取方式如下，请替换后再使用
# https://github.com/upbit/pixivpy/issues/158#issuecomment-778919084
REFRESH_TOKEN = "0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4"


# Telegram & Heroku 配置
# 你的 Telegram Bot Token
# 获取方式 @BotFather
BOT_TOKEN = ""


heroku_app_name = ""
webhook_listen = '0.0.0.0'
webhook_port = 443
webhook_url = "https://host:port/" + BOT_TOKEN
# 生成私钥和证书 openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem
webhook_key = "private.key"
webhook_cert = "cert.pem"


# Webdav 配置
encryptlist = ["https://dav.jianguoyun.com/dav/",
               ]


# For Webdav3.py
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


# For Webdav4.py
webdavdict4 = {
	"jianguoyun": {
		"baseurl": "https://dav.jianguoyun.com/dav/",
		"username": "",  # 你的账号，支持多组
		"password": ""   # 你的密码
	},
}
