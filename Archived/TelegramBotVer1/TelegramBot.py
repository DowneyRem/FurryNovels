#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import signal
import TelegramBot
import logging
import telegram.bot
from telegram.ext import messagequeue as mq
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
from telegram.utils.request import Request
from functools import wraps
from platform import platform
from PixivNovels import saveNovel, saveSeries, saveAuthor, getAuthorInfo, getSeriesId
from PrintTags import printInfo
from FileOperate import removeFile
from Convert import translate
from config import *


logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
	update.message.reply_text("""
请发送Pixiv小说链接以下载小说
使用本bot默认你已同意将下载后的小说作为 @FurryReading @FurryNovels 的更新内容
""", reply_markup=ReplyKeyboardRemove())


def help(update, context):
	update.message.reply_text("""
我是 @FurryReading @FurryNovels 的投稿bot
把Pixiv的小说链接发给我，我就可以帮你下载小说
同时我会把下载好的小说转发至 @FurryReading 作为你的分享或投稿
""")


def getIdFromURL(update, context):
	def myprint(text):
		print(text)
		update.message.reply_text(text)
	
	def getUserName(update, context):
		firstname = update.message.from_user.first_name  # 获取昵称
		lastname = update.message.from_user.name  # 获取用户名
		sharetext = "来自 {} 的分享".format(firstname)
		return sharetext
	
	def upload(path, caption):
		document = open(path, 'rb')
		name = os.path.split(path)[1]
		if caption == "":
			caption = printInfo(path)
		return document, name, caption
	
	def uploadToUser(path, caption):
		chatid = update.message.chat.id
		messageid = update.message.message_id
		myprint("开始上传")
		(document, name, caption) = upload(path, caption)
		context.bot.send_document(chatid, document, name, caption)
		# context.bot.delete_message(chatid, messageid+0)
		context.bot.delete_message(chatid, messageid+1)
		context.bot.delete_message(chatid, messageid+2)

	def uploadToChannel(path, caption):
		print("发送至频道")
		(document, name, caption) = upload(path, caption)
		caption += getUserName(update, context)
		context.bot.send_document("@FurryReading", document, name, caption)
		
		
	def testSeries(id):
		if getSeriesId(id)[0] is None:
			myprint("开始下载单篇小说……")
			filepath = saveNovel(id, path)
		else:
			myprint("开始下载系列小说……")
			id = getSeriesId(id)[0]
			filepath = saveSeries(id, path)
		return filepath
		
	def wrongType():
		if "频道" in string or"頻道"in string:
			myprint("关注我们的频道 @FurryNovels 可获取更新哦")
		elif "群" in string :
			myprint("群组链接： https://t.me/FurryNovels/27 ")
		else:
			myprint("输入有误，请重新输入Pixiv小说网址")
	
	def getId(update, context):
		caption = ""
		if re.search("[0-9]{5,}", string):
			id = re.search("[0-9]+", string).group()
			if "pixiv.net" in string:
				if "novel/series" in string:
					myprint("开始下载系列小说……")
					filepath = saveSeries(id, path)
				elif "novel" in string:
					filepath = testSeries(id)
				elif "users" in string:
					myprint("开始下载此作者的全部小说")
					caption = getAuthorInfo(id)
					filepath = saveAuthor(id, path)
				elif "artworks" in string:
					myprint("不支持下载插画，请重新输入")
			else:
				filepath = testSeries(id)
			return filepath ,caption
		else:
			wrongType()
	
	# removeFile(path)
	string = update.message.text
	(filepath, caption) = getId(update, context)
	
	if not ".zip" in filepath:
		uploadToChannel(filepath, caption)
		
	language = update.message.from_user.language_code
	filepath = translate(filepath, language)
	uploadToUser(filepath, caption)  ##上传文件
	print("")
 
 
def error(update, context):
	logger.warning('Update "%s" caused error "%s"', update, context.error)


def ping(update, context):
	update.message.reply_text(
		"chat_id: <code>%s</code>\nlanguage_code: <code>%s</code>" % (
			update.message.chat.id,
			update.message.from_user.language_code
			), parse_mode="HTML")
	
	
def cancel(update, context):
	pass
	
	
def main():
	updater = Updater(BOT_TOKEN, use_context=True, request_kwargs=REQUESTS_KWARGS)
	if "Windows" in platform():
		updater.start_polling()
	
	elif "Linux" in platform():
		updater.start_webhook(
			listen="0.0.0.0",
			port=int(os.environ.get('PORT', 5000)),
			url_path=BOT_TOKEN,
			webhook_url=f"https://{heroku_app_name}.herokuapp.com/{BOT_TOKEN}")
	# updater.bot.set_webhook(f"https://{heroku_app_name}.herokuapp.com/{BOT_TOKEN}")
	# signal.signal(signal.SIGTERM, handler_stop_signals)
	
	dispatcher = updater.dispatcher
	dispatcher.add_handler(CommandHandler("start", start))
	dispatcher.add_handler(CommandHandler("help", help))
	dispatcher.add_handler(CommandHandler("ping", ping))
	dispatcher.add_handler(CommandHandler("cancel", cancel))
	dispatcher.add_handler(MessageHandler(Filters.text, getIdFromURL))
	# dispatcher.add_handler(MessageHandler(Filters.document, )
	dispatcher.add_error_handler(error)
	updater.idle()


if __name__ == '__main__':
	path = os.getcwd()
	path = os.path.join(path, "Novels")
	
	if "Windows" in platform():
		REQUESTS_KWARGS = {'proxy_url':'HTTPS://127.0.0.1:10808/'}
		BOT_TOKEN = TEST_TOKEN
	
	elif "Linux" in platform():
		REQUESTS_KWARGS = {}
		BOT_TOKEN = BOT_TOKEN
	
	print("Bot Run!")
	main()
