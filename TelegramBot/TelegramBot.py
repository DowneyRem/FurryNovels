#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import pytz
import logging
from platform import platform

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import messagequeue as mq
from telegram.ext import Updater, ContextTypes, Defaults, Filters, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
import telegram.utils.request
import telegram.error

from FileOperate import removeFile, saveFile, saveText, timer
from Recommend import do_recommend, url_init_recommend
from PixivClass import getUrl, PixivNovels, PixivSeries, PixivAuthor, PixivObject
from Translate import translateText, translateFile
from Webdav4 import uploadAll as uploadWebdav
from config import BOT_TOKEN, TEST_TOKEN, heroku_app_name, proxy_list


# logger = logging.getLogger(__name__)
SAVEPIXIV, = range(1)


def start(update: Update, context: ContextTypes):
	if update.message.chat.type == "supergroup":
		update.message.reply_text("使用此功能请私聊我哦")
	else:
		update.message.reply_text(
			"我是 @FurryNovels 的投稿bot。向我发送Pixiv或Linpx小说链接，我就可以帮你下载小说。\n\n"
			"如果下载的小说满足【兽人小说】【txt文件】两个条件，我会转发一份到 @FurryReading ，作为你的分享。")
		update.message.reply_text(
			"此外，向我发送 txt 文件或 docx 文件，我还可以帮你翻译成你所用的 Telegram 语言。\n\n"
			"如需指定语言请用 <code>/translate ISO 639-1 的语言代码</code>，回复文件所在消息。\n如：<code>/translate en</code> 或<code>/translate zh-cn</code>",
			parse_mode="HTML")
		update.message.reply_text("具体可以参考这篇教程： https://telegra.ph/FurryNovelsReading-04-04-07")
		
def help(update: Update, context: ContextTypes):
	return start(update, context)


def ping(update: Update, context: ContextTypes):
	update.message.reply_text(
			f"chat_id: <code>{update.message.chat.id}</code>\nlanguage_code: <code>{update.message.from_user.language_code}</code>",
			parse_mode="HTML")


def delete(update: Update, context: ContextTypes):
	if update.message.chat.id == 1348148286:
		path = os.getcwd()
		li = "backup data".split(" ")
		for dir in os.listdir(path):
			if os.path.isdir(dir) and not dir.startswith(".") and dir not in li:
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
	def myprint(*args):
		for arg in args:
			update.message.reply_text(str(arg))
			print(arg)
	
	def inputerror(error=""):
		update.message.reply_text(
			text="请在 /download 后输入 pixiv 小说链接，或回复含有 pixiv 小说链接的消息",
			reply_to_message_id=update.message.message_id)
		print("pixivFilters: 回复内容无链接")
		if error:
			logging.error(error)
		
	
	link = ""
	if update.message.text:
		language = update.message.from_user.language_code
		try:
			link = getUrl(update.message.text)
			if not link and update.message.reply_to_message:
				link = getUrl(update.message.reply_to_message.text)
		except Exception as e:
			inputerror(e)
			return ConversationHandler.END
		if not link:
			inputerror()
			return ConversationHandler.END
	
	print(f"当前网址：{link}")
	if "pixiv" in link or "/pn/" in link:
		if "user" in link:  # 去末尾s，兼容linpx
			object = PixivAuthor(link)
			info = object.setLinkInfo()
			photo = object.saveAuthorIcon()
			if os.path.exists(photo):
				update.message.chat.send_photo(open(photo, 'rb'), info, reply_markup=InlineKeyboardMarkup(
					[[
						InlineKeyboardButton("下载全部", callback_data=f"{4}:{object.author_url}"),
						# InlineKeyboardButton("精确下载", callback_data=f"{6}:{object.author_url}"),
						]]))
			else:
				update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
					[[
						InlineKeyboardButton("下载全部", callback_data=f"{4}:{object.author_url}"),
						# InlineKeyboardButton("精确下载", callback_data=f"{6}:{object.author_url}"),
					]]))
		
		elif "novel/series" in link:
			object = PixivSeries(link)
			info = object.setLinkInfo()
			update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("下载系列为txt合集", callback_data=f"{2}:{object.series_url}"),
					InlineKeyboardButton("下载系列为zip合集", callback_data=f"{3}:{object.series_url}"),
					# InlineKeyboardButton("自动选择", callback_data=f"{0}:{object.series_id}"),
					]]))
		
		elif "novel" in link or "/pn/" in link:  # 去末尾s，兼容linpx
			object = PixivNovels(link)
			info = object.setLinkInfo()
			if not object.series_id:
				update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
					[[
						InlineKeyboardButton("下载本章为txt文件", callback_data=f"{1}:{object.novel_url}"),
						InlineKeyboardButton("下载作者全部小说", callback_data=f"{4}:{object.author_url}"),
					]]))
			
			else:
				update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
					[[
						InlineKeyboardButton("下载本章为txt文件", callback_data=f"{1}:{object.novel_url}"),
						InlineKeyboardButton("下载作者全部小说", callback_data=f"{4}:{object.author_url}"),
					],  [
						InlineKeyboardButton("下载系列为txt合集", callback_data=f"{2}:{object.series_url}"),
						InlineKeyboardButton("下载系列为zip合集", callback_data=f"{3}:{object.series_url}")
					]]))
		
		elif "artworks" in link:
			myprint("不支持下载插画，请重新输入")
		# PixivIllust(id).save()
			return ConversationHandler.END
		else:
			myprint("输入有误，请重新输入")
			return ConversationHandler.END
	else:
		print("pixivFilters: 回复内容无Pixiv链接")
	return SAVEPIXIV


def savePixiv(update: Update, context: ContextTypes):
	def myprint(*args):
		for arg in args:
			try:
				query.message.edit_text(str(arg))     # 修改文字消息
				# query.message.reply_text(str(arg))
			except telegram.error.BadRequest:
				query.message.edit_caption(str(arg))  # 修改图片 caption
			except Exception as e:
				logging.error(e)
			print(arg)
	
	@timer
	def uploadToUser(path, info):
		chatid = query.message.chat_id
		print(f"UploadTo: {username} ({userid})")
		query.message.chat.send_document(open(path, 'rb'), os.path.basename(path), info)
		
		try:
			context.bot.delete_message(chatid, query.message.message_id)
		except telegram.error.BadRequest as e:
			logging.error(e)
		if "group" in query.message.chat.type and query.message.reply_to_message:
			try:
				context.bot.delete_message(chatid, query.message.reply_to_message.message_id)
			except telegram.error.BadRequest as e:
				logging.error(e)
	
	
	@timer
	def uploadToChannel(channel, path, info):
		print(f"上传至频道：{channel}")
		context.bot.send_document(channel, open(path, 'rb'), os.path.basename(path), info)
	
	
	def sendMsgToChannel(channel, message):
		context.bot.send_message(channel, message, parse_mode="HTML")
	
	
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
		novel_id = object.novel_id
		return result, score, novel_id
		
	@timer
	def upload(query):
		((path1, info1, furry), (path2, info2, furry2)), score, novel_id = download(query)
		print("上传文件路径：", path1, path2, sep="\n")
		
		uploadToUser(path1, info1)
		if path2:
			uploadToUser(path2, info2)
		
		info = f"{info1}\n\n来自 {username} 的分享\n"  # info 后半部分
		if score > -100:
			info += f"推荐指数： {score} (仅供参考)\n"
		info += f"喜欢还请去Pixiv收藏或评论，以支持作者 @FurryNovels"
		info2 = info.replace(info1, info2)
		
		infolist = info1.split("\n")  # logs
		log = f" <a href='tg://user?id={userid}'>{username}</a> #U{userid}\n{infolist[0]}\n{infolist[1]}\n{infolist[2]}"
		if infolist[2] != infolist[-1]:
			log += f"\n{infolist[-1]}"
		
		if "Windows" in platform():  # 测试用
			uploadToChannel("-1001286539630", path1, info)
			if path2:
				uploadToChannel("-1001286539630", path2, info2)
			sendMsgToChannel("-1001286539630", f"#测试 {log}")
			
		elif furry >= 2 and ".zip" not in path1:  # 兽人小说 txt
			sendMsgToChannel("-1001286539630", f"#兽人小说 {log}")
			uploadToChannel("@FurryReading", path1, info)
			if path2:  # 上传翻译文件
				uploadToChannel("@FurryReading", path2, info2)
				
			if "zh" in info and score >= 6:  # 中文优秀非机翻小说
				uploadToChannel("@FurryNovels", path1, info)
				uploadWebdav(path1, "小说")
		
		elif furry >= 2 and ".zip" in path1:  # 兽人小说 zip
			sendMsgToChannel("-1001286539630", f"#兽人小说 {log}")
		elif ".zip" in path1:  # 作者合集 zip
			sendMsgToChannel("-1001286539630", f"#作者合集 {log}")
		else:  # 非兽人小说
			sendMsgToChannel("-1001286539630", f"#非兽人小说 {log}")
		
		if True:  # 友情提示
			query.message.chat.send_message("还请去Pixiv，给作者一个收藏/评论，以表支持")
			time.sleep(5)
			try:
				if not path2:
					context.bot.delete_message(query.message.chat.id, query.message.message_id + 2)
				else:
					context.bot.delete_message(query.message.chat.id, query.message.message_id + 3)
			except telegram.utils.request.BadRequest as e:
				logging.error(e)
			except Exception as e:
				logging.error(e)
				
	
	query = update.callback_query
	userid = query.message.chat.id
	username = query.from_user.first_name
	language = query.from_user.language_code
	if "zh-hans" in language:
		language = "zh_cn"
	elif "zh-hant" in language:
		language = "zh_tw"
	print(f"当前语言：{language}")
	if query.data != "":  # 清除按钮
		query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
	upload(query)
	return ConversationHandler.END
	

def timeoutcb(update: Update, context: ContextTypes):
	print(f"Conversation timed out: uid={context.user_data['uid']}")
	context.user_data.clear()
	# return ConversationHandler.END


def transFile(update: Update, context: ContextTypes):
	chatid = update.message.chat.id
	userid = update.message.from_user.id
	username = update.message.from_user.first_name
	lang2 = update.message.from_user.language_code
	message = f"请求者：<a href='tg://user?id={userid}'>{username}</a> #UID{userid}\n"
	
	text = update.message.text.lower().strip().replace("/translate", "")
	if text:  # 当前消息指定语言，回复消息指定文件
		lang2 = text.replace("-", "_").strip()
	if "zh-hans" in lang2:
		lang2 = "zh_cn"
	elif "zh-hant" in lang2:
		lang2 = "zh_tw"
	
	if update.message.document:  # 直接上传文件
		file = context.bot.get_file(update.message.document.file_id)
		name = update.message.document.file_name
		caption = update.message.caption
	elif update.message.reply_to_message and update.message.reply_to_message.document:
		file = context.bot.get_file(update.message.reply_to_message.document.file_id)
		name = update.message.reply_to_message.document.file_name
		caption = update.message.reply_to_message.caption
	else:
		update.message.reply_text(
			text="请直接发送文件或用<code> /translate zh_cn </code>回复文件所在消息",
			reply_to_message_id=update.message.message_id, parse_mode="HTML")
		print(f"transFile: {username} 未发送或回复文件，结束翻译")
		return
	
	extname = os.path.splitext(name)[1].replace(".", "")
	path = os.path.join(os.getcwd(), "Translation", "Download", name)
	print(f"transFile: 正在将 {name} 翻译成 {lang2} ")
	
	try:
		saveText(path, "")  # 保存空文件后再覆盖
		file.download(custom_path=path)
	except Exception as e:
		update.message.reply_text(f"出现未知错误1，已向管理发送错误信息")
		message = f"#下载错误 #{extname}_{lang2} {name}\n{message}\n{e}"
		logging.error(e)
		if "Windows" in platform():
			message = f"#测试 {message}"
		print(f"transFile: 下载错误，结束翻译")
		return
		
	try:
		path = translateFile(path, lang2)
		caption, lang1 = translateText(caption, lang2=lang2, mode=1)
		caption = caption.replace(lang1, lang2)
	except AttributeError as e:
		update.message.reply_text(f"无法打开当前类型的文件\n仅支持 txt 和 docx 文件")
		message = f"#无法翻译 #{extname}_{lang2} {name}\n{message}"
	except RuntimeError as e:
		update.message.reply_text(f"该文件已与你当前所用语言一致，故未翻译，如需翻译请更换 Telegram 语言包")
		message = f"#无需翻译 #{extname}_{lang2} {name}\n{message}"
	except Exception as e:
		update.message.reply_text(f"出现未知错误2，已向管理发送错误信息")
		message = f"#翻译错误 #{extname}_{lang2} {name}\n{message}\n{e}"
		logging.error(e)
	else:
		context.bot.send_document(chatid, open(path, 'rb'), os.path.basename(path), caption)
		if "zh" in lang2:
			uploadWebdav(path, "翻译")
		message = f"#已经翻译 #{lang2}_{extname} {name}\n{message}"
		print(f"翻译完成：{path}")
	finally:
		if "Windows" in platform():
			message = f"#测试 {message}"
		context.bot.send_message("-1001286539630", message, parse_mode="HTML")
	

def main():
	defaults = Defaults(
		disable_notification=True,
		disable_web_page_preview=True,
		tzinfo=pytz.timezone('Asia/Shanghai'),
		)
	updater = Updater(BOT_TOKEN, use_context=True, defaults=defaults, request_kwargs=REQUESTS_KWARGS)
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
	updater.dispatcher.add_handler(CommandHandler("translate", transFile))
	updater.dispatcher.add_handler(MessageHandler(Filters.document, transFile))
	
	updater.dispatcher.add_handler(ConversationHandler(
		entry_points=[
			CommandHandler("download", pixivFilters),
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
	try:
		main()
	except telegram.error.NetworkError as e:
		logging.warning(e)
