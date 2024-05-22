#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import requests

# from configuration import BOT_TOKEN, TEST_CHANNEL, testMode
from .configuration import BOT_TOKEN, TEST_CHANNEL, testMode
token = BOT_TOKEN


def sendMessage(token: str, chat_id: [str, int], text: str):
	params = {
		"chat_id": chat_id,
		"text": text,
		"parse_mode": "html",
		"disable_notification": True,
		"disable_web_page_preview": True,
	}
	result = requests.get(f"https://api.telegram.org/bot{token}/sendMessage", params=params)
	# print(result.json())
	if not result.json()["ok"]:
		raise Exception(f"{text}发送失败")
	
	
def sendDocument(token: str, chat_id: [str, int], file: str, caption=""):
	filename = os.path.basename(file)
	form = [
		("chat_id", (None, chat_id)),
		("document", (filename, open(file, "rb")))
	]
	if caption:
		form.append(("caption", (None, caption)))
	result = requests.post(f"https://api.telegram.org/bot{token}/sendDocument", files=form)
	# print(result.json())
	if not result.json()["ok"]:
		raise Exception(f"{filename}发送失败")


def sendMsgToChannel(chat_id: [str, int], text):
	if "test" in str(chat_id).lower():
		chat_id = TEST_CHANNEL
	sendMessage(token, chat_id, text)
	

def uploadToChannel(chat_id: [str, int], file: str, caption: str):
	if "test" in str(chat_id).lower():
		chat_id = TEST_CHANNEL
	sendDocument(token, chat_id, file, caption)
	print(f"{os.path.basename(file)} 已上传至 {chat_id}")
	

def test():
	print("测试")
	
	
if __name__ == '__main__':
	if testMode:
		test()
	