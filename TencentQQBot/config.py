# -*- coding:utf-8 -*-
import re
from nonebot.default_config import *


# 超级用户
SUPERUSERS = {

# 命令头
COMMAND_START = ['', re.compile(r'[/／!！]+')]

# bot 昵称
NICKNAME = {}

# WS默认监听的 IP 和端口
HOST = '127.0.0.1'
PORT = 8080

# 使用 HTTP 通信
# API_ROOT = 'http://127.0.0.1:8080'  # 允许调用CQHttp接口
API_ROOT = 'http://127.0.0.1:5700'  # 允许调用CQHttp接口