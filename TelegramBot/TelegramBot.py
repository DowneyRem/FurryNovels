#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import signal
import logging
from platform import platform

from telegram.ext import messagequeue as mq
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
# from telegram.utils.request import Request

from PixivNovels import (saveNovel, saveSeriesAsTxt, saveSeriesAsZip, saveAuthor, getNovelInfo,  getSeriesInfo, getAuthorInfo, getSeriesId, getTags, set2Text, novelAnalyse, seriesAnalyse, formatNovelInfo, formatSeriesInfo)
from PrintTags import printInfo, getInfo
from FileOperate import removeFile, zipFile, unzipFile, timethis
from Convert import convert
from Webdav4 import uploadAll as uploadWebdav
from DictRace import racedict
from config import *


logging.basicConfig(level=logging.INFO,
		format='%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s',
		datefmt='%Y.%m.%d. %H:%M:%S',
		# filename='parser_result.log',
		# filemode='w'
)
logger = logging.getLogger(__name__)



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


def download(update, context):
	def myprint(text):
		print(text)
		query.message.chat.send_message(text)
	
	
	@timethis
	def downloadAll(query):
		data = query.data
		method = int(data[0])
		id = data[2:] #传入的id已做过分类处理
		(filepath, caption, recommend) = downloadA(method, id)
		upload(filepath, caption, recommend)


	def downloadA(method, id):
		caption = ""
		recommend = -100
		if method == 1:
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
			text = " "  # 为了快速上传，不检测正文；避免后续报错，text不为空
			caption = getInfo(text, textlist)
			recommend = seriesAnalyse(id)
		
		elif method == 4:
			myprint("下载作者小说zip合集中……")
			filepath = saveAuthor(id, path)
			myprint("下载完成，等待上传中……")
			caption = getAuthorInfo(id)[0]
			print(caption)
		
		recommend = round(recommend, 2)
		return filepath, caption, recommend
	
	
	@timethis
	def uploadToUser(path, caption):
		username = query.message.chat.first_name
		id = query.message.chat.id
		print("上传至用户：{} ({})".format(username, id))
		document = open(path, 'rb')
		name = os.path.split(path)[1]
		query.message.chat.send_document(document, name, caption)
		
		chatid = query.message.chat.id
		messageid = query.message.message_id
		# context.bot.delete_message(chatid, messageid -1)
		context.bot.delete_message(chatid, messageid + 0)
		context.bot.delete_message(chatid, messageid + 1)
		context.bot.delete_message(chatid, messageid + 2)
	
	
	@timethis
	def uploadToChannel(channel, path, caption):
		print("上传至频道：{}".format(channel))
		document = open(path, 'rb')
		name = os.path.split(path)[1]
		context.bot.send_document(channel, document, name, caption)
	
	
	def sendMsgToChannel(channel, caption, msg=""):
		name = caption.split("\n")[0]
		link = caption.split("\n")[-4]
		username = query.message.chat.first_name.replace(" ","")
		id = query.message.chat.id
		message = f"{msg} #{username} #u{id}\n{name}\n{link}"
		context.bot.send_message(channel, message, disable_web_page_preview=1, disable_notification=0)
	
	
	def furry(caption):
		furrynum = 0
		racelist = list(racedict.values())
		# racelist = list(raceset)
		for i in range(len(racelist)):
			race = racelist[i]
			if race in caption:
				furrynum += 1
		
		if "Furry" in caption or "furry" in caption or "kemono" in caption:
			furrynum += 5
		print("福瑞指数：{}".format(furrynum))
		return furrynum
	
	
	@timethis
	def upload(filepath, caption, recommend):
		uploadToUser(filepath, caption)
		
		furrynum = furry(caption)
		username = query.message.chat.first_name
		caption += "\n来自 {} 的分享".format(username)
		if recommend > -100:
			caption += "\n推荐指数： {} @FurryNovels".format(recommend)
			
		if "Windows" in platform():  # 测试用频道
			uploadToChannel("-1001286539630", filepath, caption)
			sendMsgToChannel("-1001286539630", caption, msg="#测试")
		elif furrynum >= 3 and (".zip" not in filepath):  # 兽人小说且不为zip
			uploadToChannel("@FurryReading", filepath, caption)
			sendMsgToChannel("-1001286539630", caption, msg="#兽人小说")
			uploadWebdav(filepath)
			
			if "zh" in caption and recommend >= 7:  # 中文，优秀，小说
				uploadToChannel("@FurryNovels", filepath, caption)
		else:
			sendMsgToChannel("-1001286539630", caption, msg="#非兽人小说")
		print("")
	
	
	query = update.callback_query
	if query.data != "":  # 清除按钮
		query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
	# print(query.message)
	downloadAll(query)


def botmain(update, context):
	def myprint(text):
		print(text)
		update.message.reply_text(text)
	
	
	def wrongType(text):
		if "频道" in text or "頻道" in text:
			myprint("欢迎关注我们的频道 @FurryNovels @FurryReading")
		elif "群" in text:
			myprint("群组链接： https://t.me/FurryNovels/27")
		elif "分享" in text or "投稿" in text or "下载" in text:
			myprint("向我发送 Pixiv 的小说链接就可以了")
		elif "你好" in text:
			myprint("不用向我问好，向我发送 Pixiv 的小说链接就行")
		else:
			myprint("""请发送 Pixiv/Linpx 小说链接，如：
https://pixiv.net/novels/show.php?id=15426800
https://furrynovel.xyz/pixiv/novel/15426800
""")
	
	
	def testSeries(novel_id):
		user_id = getNovelInfo(novel_id)[6]
		(title, author, caption) = getNovelInfo(novel_id)[0:3]
		tags = getTags(novel_id, set())
		tags = set2Text(tags)
		text = "{}\n作者：{}\n标签：{}".format(title, author, tags)
		
		if getSeriesId(novel_id)[0] is None:
			update.message.reply_text(text, reply_markup=InlineKeyboardMarkup([[
			InlineKeyboardButton("下载本章为txt文件", callback_data="{}:{}".format(1, novel_id)),
			InlineKeyboardButton("下载此作者全部小说", callback_data="{}:{}".format(4, user_id)),
				]]),disable_web_page_preview=1)
		
		else:
			series_id = getSeriesId(novel_id)[0]
			(title, author, caption, count)  = getSeriesInfo(series_id)[0:4]
			text += "\n\n系列：{}，共{}篇\n".format(title, count)
			update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(
		[[
			InlineKeyboardButton("下载本章为txt文件", callback_data="{}:{}".format(1, novel_id)),
			InlineKeyboardButton("下载此作者全部小说", callback_data="{}:{}".format(4, user_id)),
		], [
			InlineKeyboardButton("下载系列为txt合集", callback_data="{}:{}".format(2, series_id)),
			InlineKeyboardButton("下载系列为zip合集", callback_data="{}:{}".format(3, series_id)),
		]]))
			
			
	def saveSeries(series_id):
		(title, author, caption, count) = getSeriesInfo(series_id)[0:4]
		text = "系列：{}，共{}篇\nBy {}\n\n{}".format(title, count, author, caption)
		update.message.reply_text(text, reply_markup=InlineKeyboardMarkup([[
			InlineKeyboardButton("下载系列为txt合集", callback_data="{}:{}".format(2, series_id)),
			InlineKeyboardButton("下载系列为zip合集", callback_data="{}:{}".format(3, series_id)),
		]]))
		
		
	def saveAuthor(user_id):
		photo = open(getAuthorInfo(user_id)[1], 'rb')
		caption = getAuthorInfo(user_id)[0]
		update.message.chat.send_photo(photo, caption,reply_markup=InlineKeyboardMarkup([[
		    InlineKeyboardButton("下载此作者全部小说", callback_data="{}:{}".format(4, user_id)),
		    # InlineKeyboardButton("精确下载", callback_data="{}:{}".format(6, user_id)),
	    ]]))

	
	def savePixiv(text, id):  # 支持Pixiv与linpx
		if "pixiv" in text:
			if "user" in text:  #去末尾s，兼容linpx
				saveAuthor(id)
			elif "novel/series" in text:
				saveSeries(id)
			elif "novel" in text:
				testSeries(id)
			elif "artworks" in text:
				myprint("不支持下载插画，请重新输入")
		elif "/pn/" in text or text == id:  # 兼容linpx分享链接
			testSeries(id)
		else:
			wrongType(text)
		
	
	def getId(update, context):
		text = update.message.text
		messageid = update.message.message_id
		
		pat = "(?:https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"
		if re.findall(pat, text) and re.findall("[0-9]{5,}", text):   # 获取网址链接
			text = re.findall(pat, text)[0]
			id = re.findall("[0-9]{5,}", text)[0]
			savePixiv(text, id)  #支持Pixiv与linpx
			
		elif re.findall("[0-9]{5,}", text):   # 兼容小说id
			pat = "[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]"
			text = re.findall(pat, text)[0]
			id = re.findall("[0-9]{5,}", text)[0]
			if re.findall(pat, text):
				savePixiv(text,id)
		else:
			wrongType(text)
	
	try:
		getId(update, context)
	except AttributeError as e:
		logging.info(e)


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
