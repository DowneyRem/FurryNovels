#!/usr/bin/python
# -*- coding: UTF-8 -*-
from opencc import OpenCC
cc1 = OpenCC('tw2sp.json')  # 繁转简
cc2 = OpenCC('s2twp.json')  # 簡轉繁


# Pixiv refresh token
# get your refresh_token, and replace REFRESH_TOKEN
# https://github.com/upbit/pixivpy/issues/158#issuecomment-778919084
REFRESH_TOKEN = "0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4"


# Telegram Bot Token
BOT_TOKEN = "5215285328:AAEtwcWrYlnWjnnobC6jVtNd-RFfx7EQMk0"
TEST_TOKEN = "5115165077:AAHhMewV12m5OUg_NeT8BA5XMxISThn0YEY"


heroku_app_name = "kjsahfkjsdhfkjdsf"
webhook_listen = '0.0.0.0'
webhook_port = 443
webhook_url = "https://host:port/" + BOT_TOKEN

# 生成私钥和证书 openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem
webhook_key = "private.key"
webhook_cert = "cert.pem"
