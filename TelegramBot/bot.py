#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import telegram.bot
from telegram.ext import messagequeue as mq
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
from telegram.utils.request import Request
from Novels import saveNovel, saveSeries, saveAll, getUserInfo, getSeriesFromNovel
from PrintTags import printInfo


## 请将TOKEN换成自己的TOKEN
## 此ROKEN将在完全测试后注销
# TOKEN = "5115165077:AAFlZXmA86PT6LiwU1hWbQYlwXTpCvpBnlI"



def start(update, context):
	update.message.reply_text('请发送Pixiv小说链接',
	                          reply_markup=ReplyKeyboardRemove())


def getIdFromURL(update, context):
	def myprint(*text):
		print(*text)
		update.message.reply_text(*text)
		
	def upload(path, caption):
		chatid = update.message.chat.id
		messageid = update.message.message_id
		myprint("开始上传")
		
		document = open(path, 'rb')
		name = os.path.split(path)[1]
		if caption == "":
			caption = printInfo(path)
		context.bot.send_document(chatid, document, name, caption)
		context.bot.delete_message(chatid, messageid+1)
		context.bot.delete_message(chatid, messageid+2)
		return messageid+3
		
		
	def testSeries(id):
		if getSeriesFromNovel(id)[0] is None:
			myprint("开始下载单篇小说……")
			filepath = saveNovel(id, path)
		else:
			myprint("该小说为系列小说")
			myprint("开始下载系列小说……")
			id = getSeriesFromNovel(id)[0]
			filepath = saveSeries(id, path)
		return filepath
		
		
		
	def wrongType():
		if "频道" in string or"頻道"in string:
			myprint("关注我们的频道 @FurryNovels 可获取更新哦")
		elif "群" in string :
			myprint("群组链接： https://t.me/FurryNovels/27 ")
		else:
			myprint("输入有误，请重新输入Pixiv小说网址")
	
	
	caption = ""
	string = update.message.text
	if re.search("[0-9]+", string):
		id = re.search("[0-9]+", string).group()
		if "pixiv.net" in string:
			if "novel/series" in string:
				myprint("开始下载系列小说……")
				filepath = saveSeries(id, path)
			elif "novel" in string:
				filepath = testSeries(id)
			elif "users" in string:
				myprint("开始下载此作者的全部小说")
				caption = getUserInfo(id)
				# myprint(caption)
				filepath = saveAll(id, path)
			elif "artworks" in string:
				myprint("不支持下载插画，请重新输入")
				
		elif re.search("[0-9]+", string):
			filepath = testSeries(id)
		else:
			wrongType()
		upload(filepath, caption)  ##上传文件
	else:
		wrongType()


def ping(update, context):
	update.message.reply_text("chat_id: <code>%s</code>\nlanguage_code: <code>%s</code>" % (
		update.message.chat.id,
		update.message.from_user.language_code
		), parse_mode="HTML")


def main():
	updater = Updater(TOKEN, use_context=True, request_kwargs={
		'proxy_url': 'HTTPS://127.0.0.1:10808/'
		})
	
	dispatcher = updater.dispatcher
	dispatcher.add_handler(CommandHandler("start", start))
	dispatcher.add_handler(CommandHandler("ping", ping))
	dispatcher.add_handler(MessageHandler(Filters.text, getIdFromURL))

	
	dispatcher.add_error_handler(error)
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	path = os.getcwd()
	path = os.path.join(path, "Novels")
	print("Bot Run!")
	main()
