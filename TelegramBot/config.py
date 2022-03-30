#!/usr/bin/python
# -*- coding: UTF-8 -*-

from opencc import OpenCC
# 官方的 OpenCC
# cc1 = OpenCC('tw2sp.json')  # 繁转简
# cc2 = OpenCC('s2twp.json')  # 簡轉繁

# opencc-python-reimplemented
cc1 = OpenCC('tw2sp')  # 繁转简
cc2 = OpenCC('s2twp')  # 簡轉繁


# 你的Telegram Bot Token
# 获取方式 @BotFather
BOT_TOKEN = ""


# 你的 Pixiv REFRESH_TOKEN
# 获取方式如下，请替换后再使用
# https://github.com/upbit/pixivpy/issues/158#issuecomment-778919084
REFRESH_TOKEN = "0zeYA-PllRYp1tfrsq_w3vHGU1rPy237JMf5oDt73c4"

