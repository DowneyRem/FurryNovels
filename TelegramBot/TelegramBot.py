#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import logging
from platform import platform

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import messagequeue as mq
from telegram.ext import ContextTypes, Updater, Filters, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
from telegram.utils.request import Request
import telegram.error

from FileOperate import removeFile, timer
from Recommend import do_recommend, url_init_recommend
from PixivClass import getId, PixivNovels, PixivSeries, PixivAuthor
from Webdav4 import uploadAll as uploadWebdav
from config import BOT_TOKEN, TEST_TOKEN, heroku_app_name, proxy_list


# logger = logging.getLogger(__name__)
SAVEPIXIV, = range(1)


def start(update: Update, context: ContextTypes):
	if update.message.chat.type == "supergroup":
		update.message.reply_text("使用此功能请私聊我哦")
	else:
		# chatid = update.message.chat.id
		update.message.reply_text("我是 @FurryNovels 的投稿bot，发送Pixiv或Linpx小说链接，我就可以帮你下载小说", disable_notification=1)
		update.message.reply_text("如果下载内容满足【兽人小说】【txt文件】两个条件，我会转发一份到 @FurryReading ，作为你的分享", disable_notification=1)


def help(update: Update, context: ContextTypes):
	return start(update, context)


def ping(update: Update, context: ContextTypes):
	update.message.reply_text(
			f"chat_id: <code>{update.message.chat.id}</code>\nlanguage_code: <code>{update.message.from_user.language_code}</code>",
			parse_mode="HTML")


def delete(update: Update, context: ContextTypes):
	if update.message.chat.id == 1348148286:
		path = os.getcwd()
		for dir in os.listdir(path):
			if os.path.isdir(dir) and not dir.startswith("."):
				directory = os.path.join(path, dir)
				removeFile(directory)
				print(f"已删除：{directory}")
				update.message.reply_text(f"已删除：{dir}")
		update.message.reply_text("删除完成")


def cancel(update: Update, context: ContextTypes):
	# update.message.reply_text("已取消")
	pass


# def error(update: Update, context: ContextTypes):
# 	logger.warning('Update "%s" caused error "%s"', update: Update, context.error)


def pixivFilters(update: Update, context: ContextTypes):
	string = update.message.text
	message_id = update.message.message_id
	language = update.message.from_user.language_code
	
	def myprint(*args):
		for arg in args:
			update.message.reply_text(arg)
			print(arg)
	
	if ("pixiv" in string or "/pn/" in string):
		id = getId(string)
		
		if "user" in string:  # 去末尾s，兼容linpx
			object = PixivAuthor(id)
			info = object.setLinkInfo()
			photo = open(object.saveAuthorIcon(), 'rb')
			update.message.chat.send_photo(photo, info, reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("下载全部", callback_data=f"{4}:{object.author_id}"),
					# InlineKeyboardButton("精确下载", callback_data=f"{6}:{object.author_id}"),
					]]))
		
		elif "novel/series" in string:
			object = PixivSeries(id)
			info = object.setLinkInfo()
			update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("下载系列为txt合集", callback_data=f"{2}:{object.series_id}"),
					InlineKeyboardButton("下载系列为zip合集", callback_data=f"{3}:{object.series_id}"),
					# InlineKeyboardButton("自动选择", callback_data=f"{0}:{object.series_id}"),
					]]))
		
		elif "novel" in string:  # 去末尾s，兼容linpx
			object = PixivNovels(id)
			info = object.setLinkInfo()
			if not object.series_id:
				update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
					[[
						InlineKeyboardButton("下载本章为txt文件", callback_data=f"{1}:{object.novel_id}"),
						InlineKeyboardButton("下载作者全部小说", callback_data=f"{4}:{object.author_id}"),
					]]))
			
			else:
				update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
					[[
						InlineKeyboardButton("下载本章为txt文件", callback_data=f"{1}:{object.novel_id}"),
						InlineKeyboardButton("下载作者全部小说", callback_data=f"{4}:{object.author_id}"),
					],  [
						InlineKeyboardButton("下载系列为txt合集", callback_data=f"{2}:{object.series_id}"),
						InlineKeyboardButton("下载系列为zip合集", callback_data=f"{3}:{object.series_id}")
					]]))
		
		elif "artworks" in string:
			myprint("不支持下载插画，请重新输入")
		# PixivIllust(id).save()
		else:
			myprint("输入有误，请重新输入")
	return SAVEPIXIV


def savePixiv(update: Update, context: ContextTypes):
	def myprint(*args):
		for arg in args:
			query.message.reply_text(arg)
			print(arg)
	
	@timer
	def uploadToUser(path, info):
		# username = query.message.chat.first_name
		# userid = query.message.chat.id
		chatid = query.message.chat.id
		messageid = query.message.message_id
		print(f"UploadTo: {username} ({userid})")
		query.message.chat.send_document(open(path, 'rb'), os.path.basename(path), info)
		# context.bot.send_document(chatid, open(path, 'rb'), os.path.basename(path), info)
		
		try:
			pass
			# context.bot.delete_message(chatid, messageid -1)
			context.bot.delete_message(chatid, messageid + 0)
			context.bot.delete_message(chatid, messageid + 1)
			context.bot.delete_message(chatid, messageid + 2)
		except telegram.error.BadRequest:
			pass
	
	
	@timer
	def uploadToChannel(channel, path, info):
		print(f"上传至频道：{channel}")
		context.bot.send_document(channel, open(path, 'rb'), os.path.basename(path), info)
	
	
	def sendMsgToChannel(channel, message):
		context.bot.send_message(channel, message, parse_mode="HTML", disable_web_page_preview=1, disable_notification=1, )
	
	
	def download(query):
		method, id = int(query.data[0]), query.data[2:]
		result, score, furry = "", "", ""
		if method == 1:
			myprint("正在下载当前章节……")
			object = PixivNovels(id)
			result = object.save(lang2=language)
		elif method == 2:
			myprint("正在下载txt合集中……")
			object = PixivSeries(id)
			result = object.saveAsTxt(lang2=language)
		elif method == 3:
			myprint("正在下载zip合集中……")
			object = PixivSeries(id)
			result = object.saveAsZip(lang2=language)
		elif method == 4:
			myprint("正在下载此作者全部小说……")
			object = PixivAuthor(id)
			result = object.save(lang2=language)
		else:
			pass
		myprint("下载完成，等待上传中……")
		score = object.score
		furry = object.furry_score
		novel_id = object.novel_id
		return result, score, furry, novel_id
		
		
	@timer
	def upload(query):
		((path1, info1), (path2, info2)), score, furry, novel_id = download(query)
		
		uploadToUser(path1, info1)
		if path2:
			uploadToUser(path2, info2)
		
		info = f"{info1}\n\n来自 {username} 的分享\n"
		if score > -100:
			info += f"推荐指数： {score} (仅供参考)\n"
		info += f"喜欢还请去Pixiv收藏或评论，以支持作者 @FurryNovels"
		info2 = info.replace(info1, info2)
		
		infolist = info1.split("\n")
		log = f" <a href='tg://user?id={userid}'>{username}</a> #U{userid}\n{infolist[0]}\n{infolist[1]}\n{infolist[2]}"
		if infolist[2] != infolist[-1]:
			log += f"\n{infolist[-1]}"
		
		if "Windows" in platform():  # 测试用
			uploadToChannel("-1001286539630", path1, info)
			if path2:
				uploadToChannel("-1001286539630", path1, info)
			sendMsgToChannel("-1001286539630", f"#测试 {log}")
			
		elif furry >= 3 and ".zip" not in path1:  # 兽人小说 txt
			uploadToChannel("@FurryReading", path1, info)
			sendMsgToChannel("-1001286539630", f"#兽人小说 {log}")
			if path2:  # 上传翻译文件
				uploadToChannel("@FurryReading", path2, info2)
				
			if "zh" in info and score >= 7:  # 中文优秀非机翻小说
				uploadToChannel("@FurryNovels", path1, info)
				uploadWebdav(path1)
		
		elif furry >= 3 and ".zip" in path1:  # 兽人小说 zip
			sendMsgToChannel("-1001286539630", f"#兽人小说 {log}")
		else:  #非兽人小说
			sendMsgToChannel("-1001286539630", f"#非兽人小说 {log}")
		
		if True:  # 友情提示
			query.message.chat.send_message("还请去Pixiv，给作者一个收藏/评论，以表支持")
			time.sleep(5)
		if not path2:
			context.bot.delete_message(query.message.chat.id, query.message.message_id + 4)
		else:
			context.bot.delete_message(query.message.chat.id, query.message.message_id + 5)
	
	
	query = update.callback_query
	userid = query.message.chat.id
	username = query.from_user.first_name
	language = query.from_user.language_code
	if "zh-hans" in language:
		language = "zh_cn"
	elif "zh-hant" in language:
		language = "zh_tw"
	if query.data != "":  # 清除按钮
		query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
	upload(query)
	return ConversationHandler.END
	

def timeoutcb(update: Update, context: ContextTypes):
	print(f"Conversation timed out: uid={context.user_data['uid']}")
	context.user_data.clear()


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
	
	updater.dispatcher.add_handler(CommandHandler("start", start))
	updater.dispatcher.add_handler(CommandHandler("help", help))
	updater.dispatcher.add_handler(CommandHandler("ping", ping))
	updater.dispatcher.add_handler(CommandHandler("cancel", cancel))
	updater.dispatcher.add_handler(CommandHandler("delete", delete))
	updater.dispatcher.add_handler(ConversationHandler(
		entry_points=[
			MessageHandler(Filters.regex('[pixiv, pn].+[0-9]{5,}'), pixivFilters),
			],
		states={
			SAVEPIXIV: [
				CallbackQueryHandler(savePixiv, pattern=".+"),
				],
			ConversationHandler.TIMEOUT: [MessageHandler(None, timeoutcb)],
			},
		fallbacks=[],
		conversation_timeout=300,
		))
	
	# updater.dispatcher.add_handler(MessageHandler(Filters.document, )
	# updater.dispatcher.add_error_handler(error)
	updater.idle()


if __name__ == '__main__':
	path = os.getcwd()
	path = os.path.join(path, "Novels")
	
	if "Windows" in platform():
		# REQUESTS_KWARGS = {'proxy_url':'HTTPS://127.0.0.1:10808/'}
		REQUESTS_KWARGS = {'proxy_url': proxy_list[0]}
		BOT_TOKEN = TEST_TOKEN  # 使用测试bot
	
	elif "Linux" in platform():
		REQUESTS_KWARGS = {}
		BOT_TOKEN = BOT_TOKEN
	
	print("Bot Runs!")
	main()
