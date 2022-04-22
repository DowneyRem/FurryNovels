#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import signal
import logging
from functools import wraps
from platform import platform

from telegram.ext import messagequeue as mq
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
# from telegram.utils.request import Request

from PixivNovels import (saveNovel, saveSeriesAsTxt, saveSeriesAsZip, saveAuthor, getNovelInfo, getAuthorInfo, getSeriesId, novelAnalyse, seriesAnalyse, formatNovelInfo, formatSeriesInfo)
from PrintTags import printInfo, getInfo
from FileOperate import findFile, openText, removeFile, unzipFile
from Convert import convert
from DictRace import racedict
from config import *


# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)
# logger = logging.getLogger(__name__)



def start(update, context):
	# chatid = update.message.chat.id
	# context.bot.send_message(chatid, "sadfsdf")
	update.message.reply_text("发送Pixiv的小说链接，即可下载小说")


def help(update, context):
	update.message.reply_text("""
我是 @FurryNovels 的投稿bot，把Pixiv的小说链接发给我，我就可以帮你下载小说
""")
	update.message.reply_text("""
如果下载内容同时满足【中文】【兽人小说】的【txt文件】三个条件，我会转发一份到 @FurryReading ，作为你的分享
""")


# def error(update, context):
# 	logger.warning('Update "%s" caused error "%s"', update, context.error)


def ping(update, context):
	update.message.reply_text(
		"chat_id: <code>%s</code>\nlanguage_code: <code>%s</code>" % (
			update.message.chat.id,
			update.message.from_user.language_code
			), parse_mode="HTML")


def cancel(update, context):
	# update.message.reply_text("已取消")
	pass


def download(update, context):
	def myprint(text):
		print(text)
		query.message.chat.send_message(text)
	
	
	def uploadToUser(path, caption):
		print("上传至用户")
		document = open(path, 'rb')
		name = os.path.split(path)[1]
		query.message.chat.send_document(document, name, caption)
		
		chatid = query.message.chat.id
		messageid = query.message.message_id
		# context.bot.delete_message(chatid, messageid -1)
		context.bot.delete_message(chatid, messageid +0)
		context.bot.delete_message(chatid, messageid +1)
		context.bot.delete_message(chatid, messageid +2)
		
		
	def uploadToChannel(channel, path, caption):
		print("上传至频道：{}".format(channel))
		document = open(path, 'rb')
		name = os.path.split(path)[1]
		context.bot.send_document(channel, document, name, caption)
		
	
	def downloadAll(query):
		data = query.data
		method = int(data[0])
		id = data[2:] #传入的id已做过分类处理
		
		if   method == 1:
			myprint("下载单章中……")
			filepath = saveNovel(id, path)
			myprint("下载完成，等待上传中……")
			caption = printInfo(filepath)
			recommend = novelAnalyse(id)
		
		elif method == 2:
			myprint("下载系列txt合集中……")
			filepath = saveSeriesAsTxt(id, path)
			myprint("下载完成，等待上传中……")
			caption = printInfo(filepath)
			recommend = seriesAnalyse(id)
		
		elif method == 3:
			myprint("下载系列zip合集中……")
			filepath = saveSeriesAsZip(id, path)
			myprint("下载完成，等待上传中……")
			
			caption = formatSeriesInfo(id)
			caption = caption.replace("\n", "\n\t")
			caption = caption.split("\t")
			textlist = caption[0:4]
			text = " " #为了快速上传，不检测正文；避免后续报错，text不为空
			caption = getInfo(text, textlist)
			recommend = seriesAnalyse(id)
		
		elif method == 4:
			myprint("下载作者小说zip合集中……")
			filepath = saveAuthor(id, path)
			myprint("下载完成，等待上传中……")
			caption = getAuthorInfo(id)[3]
			recommend = -100
		# elif method == 5:
		# 	pass
		
		recommend = round(recommend, 2)
		return filepath, caption, recommend
	
	
	def furry(caption):
		furrynum = 0
		racelist = list(racedict.values())
		# racelist = list(raceset)
		for i in range(len(racelist)):
			race = racelist[i]
			if race in caption:
				furrynum += 1
		print("福瑞指数：{}".format(furrynum))
		return furrynum
	
	
	query = update.callback_query
	# print(query.message)
	username = query.message.chat.first_name
	if query.data !="":  #清除按钮
		query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
	
	(filepath, caption, recommend) = downloadAll(query)
	furrynum = furry(caption)
	uploadToUser(filepath, caption)
	
	caption += "\n来自 {} 的分享".format(username)
	if recommend >= -100:
		caption += "\n推荐指数： {} ".format(recommend)
		caption += "@FurryNovels"
		
	if furrynum >= 3 and "zh" in caption and (".zip" not in filepath):
		uploadToChannel("@FurryReading", filepath, caption)
	if furrynum >= 3 and recommend >= 5 and "zh" in caption:
		# uploadToChannel("@FurryNovels", filepath, caption)
		pass
	
	
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
		messageid = update.message.message_id

		if re.search("[0-9]{5,}", string):
			id = re.search("[0-9]+", string).group()
			if "pixiv.net" in string:
				
				if "users" in string:
					saveAuthor(id)
				elif "novel/series" in string:
					myprint("开始下载系列小说……", )
					saveSeries(id)
				elif "novel" in string:
					testSeries(id)
				elif "artworks" in string:
					myprint("不支持下载插画，请重新输入")
				
			else:
				testSeries(id)
		else:
			wrongType()
	
	string = update.message.text
	getId(update, context)



def main():
	# bot = Bot(token=BOT_TOKEN)
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
	# dispatcher.add_error_handler(error)
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
