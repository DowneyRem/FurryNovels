#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import signal
import logging
from telegram.ext import messagequeue as mq
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
from telegram.utils.request import Request
from functools import wraps
from platform import platform

from PixivNovels import (saveNovel, saveSeriesAsTxt, saveSeriesAsZip, saveAuthor, getNovelInfo,getAuthorInfo, getSeriesId, novelAnalyse, seriesAnalyse, formatNovelInfo, formatSeriesInfo)
from PrintTags import printInfo, getInfo
from FileOperate import findFile, openText, removeFile
from Convert import translate
from DictRace import racedict
from config import *


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
	update.message.reply_text("发送Pixiv小说链接下载小说", reply_markup=ReplyKeyboardRemove())


def help(update, context):
	update.message.reply_text("""
我是 @FurryReading @FurryNovels 的投稿bot
把Pixiv的小说链接发给我，我就可以帮你下载小说
同时我会把下载好的小说转发至 @FurryReading 作为你的分享或投稿
""")


def error(update, context):
	logger.warning('Update "%s" caused error "%s"', update, context.error)


def ping(update, context):
	update.message.reply_text(
		"chat_id: <code>%s</code>\nlanguage_code: <code>%s</code>" % (
			update.message.chat.id,
			update.message.from_user.language_code
			), parse_mode="HTML")


def cancel(update, context):
	# update.message.reply_text("已取消")
	pass


def myprint(update, text):
	text = "ceui"
	print(text)
	try:
		update.message.reply_text(text)
		# bot.send_message(update.message.chat.id, text)
	except:
		print("uibd")
		


def download(update, context):
	query = update.callback_query
	data = query.data
	method = int(data[0])
	id = data[2:]
	
	# if query.data !="":
	# 	query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
	
	if   method == 1:
		myprint(update, "下载单章中……")
		filepath = saveNovel(id, path)
		caption  = printInfo(filepath)
		# caption  = formatNovelInfo(id)
		caption += "推荐指数：".format(novelAnalyse(id))
		
	elif method == 2:
		myprint(update, "下载系列txt合集中……")
		filepath = saveSeriesAsTxt(id, path)
		caption  = printInfo(filepath)
		# caption  = formatSeriesInfo(id)
		caption += "推荐指数：".format(seriesAnalyse(id))
		
	elif method == 3:
		myprint(update, "下载系列zip合集中……")
		filepath = saveSeriesAsZip(id, path)
		caption = printInfo(filepath)
		# caption += "推荐指数：".format(seriesAnalyse(id))
		
	elif method == 4:
		filepath = saveAuthor(id, path)
		caption = formatSeriesInfo(id)
	elif method == 5:
		pass
		
	# print(filepath)
	# print(caption)
	

def uploadFile(path):
	document = open(path, 'rb')
	name = os.path.split(path)[1]
	caption = printInfo(path)
	return document, name, caption
	

def getUserName(update, context):
	firstname = update.message.from_user.first_name  # 获取昵称
	username = update.message.from_user.username  # 获取用户名
	text = "\n来自 {} 的分享".format(firstname)
	return text
	
	
def uploadToUser(update, context):
	chatid = update.message.chat.id
	messageid = update.message.message_id
	myprint(update, "开始上传……")
	(document, name, caption) = uploadFile(path)
	context.bot.send_document(chatid, document, name, caption)
	# context.bot.delete_message(chatid, messageid + 0)
	context.bot.delete_message(chatid, messageid + 1)
	context.bot.delete_message(chatid, messageid + 2)
	print("文件已上传至用户")


def uploadToChannel(update, context, channel, path, recommend=0):
	(document, name, caption) = uploadFile(path)
	caption += getUserName(update, context)
	if recommend >= 0:
		caption += "\n推荐指数：{}".format(recommend)
		caption += " @FurryNovels"
	
	context.bot.send_document(channel, document, name, caption)
	print("已经发送至：" + channel)




def botmain(update, context):
	def myprint(text):
		print(text)
		update.message.reply_text(text)
	
	def wrongType():
		if "频道" in string or "頻道" in string:
			myprint("关注我们的频道 @FurryNovels 可获取更新哦", )
		elif "群" in string:
			myprint("群组链接： https://t.me/FurryNovels/27 ", )
		else:
			myprint("输入有误，请重新输入Pixiv小说网址", )
	
	
	def uploadToUser(path):
		chatid = update.message.chat.id
		messageid = update.message.message_id
		myprint("开始上传……")
		(document, name, caption) = uploadFile(path)
		context.bot.send_document(chatid, document, name, caption)
		# context.bot.delete_message(chatid, messageid + 0)
		context.bot.delete_message(chatid, messageid + 1)
		context.bot.delete_message(chatid, messageid + 2)
		print("文件已上传至用户")
	
	
	def testSeries(novel_id):
		if getSeriesId(novel_id)[0] is None:
			user_id = getNovelInfo(novel_id)[6]
			update.message.reply_text("请选择下载方式",
				reply_markup=InlineKeyboardMarkup([[
						InlineKeyboardButton("下载当前章节为txt文件", callback_data="{}:{}".format(1, novel_id)),
						InlineKeyboardButton("下载作者小说为zip合集", callback_data="{}:{}".format(4, user_id)),
					]]))
		
		else:
			series_id = getSeriesId(novel_id)[0]
			update.message.reply_text("请选择下载方式",
				reply_markup=InlineKeyboardMarkup([
					[
						InlineKeyboardButton("下载当前章节为txt文件", callback_data="{}:{}".format(1, novel_id)),
					], [
						InlineKeyboardButton("下载所在系列为txt合集", callback_data="{}:{}".format(2, series_id)),
						InlineKeyboardButton("下载所在系列为zip合集", callback_data="{}:{}".format(3, series_id)),
					]]))
			
			
	def saveSeries(series_id):
		update.message.reply_text("请选择下载方式",
			reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("下载系列为txt合集", callback_data="{}:{}".format(2, series_id)),
					InlineKeyboardButton("下载系列为zip合集", callback_data="{}:{}".format(3, series_id)),
				]]))
		
	def saveAuthor(user_id):
		update.message.reply_text("请选择下载方式",
			reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("查看作者简介", callback_data="{}:{}".format(5, user_id)),
					InlineKeyboardButton("下载作者小说为zip合集", callback_data="{}:{}".format(4, user_id)),
				]]))
		
	
	def getId(update, context):
		string = update.message.text
		if re.search("[0-9]{5,}", string):
			id = re.search("[0-9]+", string).group()
			if "pixiv.net" in string:
				if "novel/series" in string:
					myprint("开始下载系列小说……", )
					# (filepath, recommend) =
					saveSeries(id)
				elif "novel" in string:
					testSeries(id)
				
				elif "users" in string:
					myprint("开始下载此作者的全部小说")
					saveAuthor(id)
				elif "artworks" in string:
					myprint("不支持下载插画，请重新输入")
				download(string, id)
				
			else:
				testSeries(id)
		else:
			wrongType()
	
	string = update.message.text
	getId(update, context)





















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
	dispatcher.add_handler(MessageHandler(Filters.text, botmain))

	# dispatcher.add_handler(MessageHandler(Filters.document, )
	updater.dispatcher.add_handler(CallbackQueryHandler(download))
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
