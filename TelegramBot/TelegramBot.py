#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
import pytz
import logging
from platform import platform
from datetime import datetime
from uuid import uuid4

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent, InlineQueryResultDocument
from telegram.ext import Updater, ContextTypes, Defaults, Filters
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, InlineQueryHandler

import telegram.utils.request
import telegram.error

from FileOperate import readJson, removeFile, makeFile, timer
from PixivClass import getUrl, PixivObject
from PrintInfo import printInfo
# from PixivSearch import PixivSearch
# from Recommend import do_recommend, url_init_recommend
from Translate import translateText, transFile
from Webdav4 import uploadNovel as uploadToWebdav
from FurryNovelWeb import uploadToWebSite, getOriginalLink
from configuration import BOT_TOKEN, WEB_HOOK, proxy_list
from configuration import testMode, TEST_CHANNEL, ADMIN


logger = logging.getLogger(__name__)
SAVEPIXIV, = range(1)
SEARCH = range(1)
sourcemsg = """
开发：@DowneyRem
协助：@upanther @eatswap @windyhusky

代码开源：https://github.com/DowneyRem/FurryNovels/tree/main/TelegramBot
使用教程：https://telegra.ph/FurryNovelsReading-04-04-07
电报教程：https://telegra.ph/TNTwwxs-09-08-06
投喂打赏：https://afdian.net/@TNTwwxs
友情链接：@TNTwwxs @FurryGamesIndex @KemonoGames @FurryNovel
""".strip()


class TelegramFunction:
	pass


def start(update: Update, context: ContextTypes):
	if update.message.chat.type == "supergroup":
		update.message.reply_text("使用此功能请私聊我哦")
	else:
		update.message.reply_text(
			"我是 @FurryReading 的投稿bot。向我发送 <a href='https://www.pixiv.net/'>Pixiv</a> 或 <a href='https://furrynovel.ink/'>Linpx</a> 或 <a href='https://furrynovel.com/'>兽人控小说站</a> 的小说链接，我就可以帮你下载小说。\n\n"
			"如果下载的小说满足【兽人小说】【txt文件】两个条件，我会转发一份到 @FurryNovels ，作为你的分享。",
			parse_mode="HTML")
		update.message.reply_text(
			"此外，向我发送 txt 文件或 docx 文件，我还可以帮你翻译成你所用的 Telegram 语言。<a href='https://t.me/TNTwwxs/337'>点我查看 Telegram 语言包</a>。\n\n"
			"如需指定语言请用 <code>/translate ISO 639-1 的语言代码</code>，回复文件所在消息。\n如：<code>/translate en</code> 或 <code>/translate zh-cn</code> 或 <code>/translate zh-tw</code>",
			parse_mode="HTML")
		update.message.reply_text("具体可以查看这篇教程： https://telegra.ph/FurryNovelsReading-04-04-07")


def help(update: Update, context: ContextTypes):
	return start(update, context)


def ping(update: Update, context: ContextTypes):
	update.message.reply_text(
		f"chat_id: <code>{update.message.chat.id}</code>\n"
		f"language_code: <code>{update.message.from_user.language_code}</code>",
		parse_mode="HTML")


def source(update: Update, context: ContextTypes):
	update.message.reply_text(sourcemsg, parse_mode="HTML")


def deleteFolders(update: Update, context: ContextTypes):
	if update.message.chat.id in ADMIN:
		path = os.getcwd()
		li = "backup data".split(" ")
		for folder in os.listdir(path):
			directory = os.path.join(path, folder)
			if os.path.isdir(directory) and not folder.startswith(".") and folder not in li:
				removeFile(directory)
				print(f"已删除：{directory}")
				update.message.reply_text(f"已删除：{folder}")
		update.message.reply_text("删除完成")


def uploadToChannel(update: Update, context: ContextTypes, channel, path, info):
	print(f"上传至频道：{channel}")
	logging.info(f"上传至频道：{channel}")
	context.bot.send_document(channel, open(path, 'rb'), os.path.basename(path), info)
	
	
def cancel(update: Update, context: ContextTypes):
	# update.message.reply_text("已取消")
	pass


def error(update: Update, context: ContextTypes):
	message = f"Update {Update} caused error {context.error}"
	# logger.warning(message)
	

def myprint(update: Update, *args):
	for arg in args:
		update.message.reply_text(str(arg))
		print(arg)
		logging.info(str(arg))


class PIllust:
	pass


def getLink(update: Update):
	link = ""
	if update.message.text:
		link = getUrl(update.message.text)
		if not link and update.message.reply_to_message:
			link = getUrl(update.message.reply_to_message.text)
		if not link:
			update.message.reply_text(
				text="请在 /download 后输入 pixiv 小说链接，或回复含有 pixiv 小说链接的消息",
				reply_to_message_id=update.message.message_id)
			print("pixivFilters: 回复内容无链接2")
			logging.info("pixivFilters: 回复内容无链接2")
			return ConversationHandler.END
	return link


def downIllust(update: Update, context: ContextTypes):
	link = getLink(update)
	userid = update.message.from_user.id
	username = update.message.from_user.first_name
	if len(username) <= 2:
		username = username * 4
	
	if link:
		obj = PixivObject(link)
		info = obj.setLinkInfo()
		update.message.reply_text(info)
		
		paths = obj.save()
		# path = obj.saveAsZip()
		for path in paths:
			context.bot.send_photo(
				update.message.chat_id, open(path, 'rb'),
				caption=link, disable_notification=True)
			
			# context.bot.send_document(
			# 	update.message.chat_id,
			# 	open(path, 'rb'), filename=os.path.basename(path),
			# 	caption=link, disable_notification=True)
		
		message = f"#插画预览 <a href='tg://user?id={userid}'>{username}</a> #UID{userid}\n"
		context.bot.send_message(TEST_CHANNEL, f"{message}{info}", parse_mode="HTML")
		return ConversationHandler.END
		
	else:
		update.message.reply_text(
			text="请在 /download 后输入 pixiv 小说链接，或回复含有 pixiv 小说链接的消息",
			reply_to_message_id=update.message.message_id)
		return ConversationHandler.END
	
	
def inlineIllust(update: Update, context: ContextTypes) -> None:
	query = update.inline_query.query
	if query == "":
		return
	
	result = []
	if "artwork" in query:
		illust = PixivObject(query)
		title = illust.obj.title
		info = illust.obj.setLinkInfo()
		for i in range(len(illust.obj.original_urls)):
			result.append(
				InlineQueryResultPhoto(
					id=str(uuid4()),
					photo_url=illust.obj.original_urls[i],
					thumb_url=illust.obj.medium_urls[i],
					title=title,
					caption=query
				),
			)
		# 发送标题等信息
		# result.append(
		# 	InlineQueryResultArticle(
		# 		id=str(uuid4()), title=title,
		# 		input_message_content=InputTextMessageContent(info),
		# 	),
		# )
		
	# elif query != "":
	# 	illust = PixivObject(query)
	# 	title = illust.obj.title
	# 	result.append(
	# 		InlineQueryResultDocument(
	# 			id=str(uuid4()), title=title,
	# 			document_url=illust.saveAsZip()  # 需要URL形式的zip pdf文件
	# 		)
	# 	)
	#
	else:
		result.append(
			InlineQueryResultArticle(
				id=str(uuid4()), title="请输入 Pixiv 插画链接",
				input_message_content=InputTextMessageContent(f"Inline 模式下，请输入 Pixiv 插画链接"),
			),
		)
	update.inline_query.answer(result)
	
	userid = update.message.from_user.id
	username = update.message.from_user.first_name
	message = f"#Inline插画预览 <a href='tg://user?id={userid}'>{username}</a> #UID{userid}\n"
	context.bot.send_message(TEST_CHANNEL, f"{message}{query}", parse_mode="HTML")
	
	
class PNovel:
	pass


def downNovelsList(update, context):
	userid = update.message.chat.id
	username = update.message.from_user.first_name
	language = update.message.from_user.language_code
	if "zh-hans" in language:
		language = "zh_cn"
	elif "zh-hant" in language:
		language = "zh_tw"

	myprint(update, "正在按顺序下载当前小说，即将上传TXT合集")
	links = getLink(update)
	# myprint(update, links)
	obj = PixivObject(links)
	paths = obj.saveAsTxt(language)
	infos = obj.obj.setFileInfo(language)
	share = f"\n\n来自 {username} 的分享\n"  # info 后半部分
	if obj.score > -100:
		share += f"推荐指数： {obj.score} (仅供参考)\n"
	share += f"喜欢还请去Pixiv收藏或评论，以支持作者 @FurryReading"
	myprint(update, "喜欢还请去Pixiv，给作者一个收藏/评论，以表支持")
	
	for path, info in zip(paths, infos):
		context.bot.send_document(userid, open(path, 'rb'),
			filename=os.path.basename(path), caption=info)
		
		if testMode:  # 测试用
			context.bot.send_document(TEST_CHANNEL, open(path, 'rb'),
				filename=os.path.basename(path), caption=f"{info}{share}")
			
		elif obj.furry >= 2 and ".zip" not in path:  # 兽人小说 txt
			context.bot.send_document("@FurryNovels", open(path, 'rb'),
				filename=os.path.basename(path), caption=f"{info}{share}")
			
			if obj.furry >= 6.5:
				context.bot.send_document("@FurryReading", open(paths[0], 'rb'),
					filename=os.path.basename(path), caption=f"{infos[0]}{share}")
	
	try:
		time.sleep(3)
		chatid = update.message.chat.id
		context.bot.delete_message(chatid, update.message.message_id + 1)
		context.bot.delete_message(chatid, update.message.message_id + 2)
	except telegram.error.BadRequest as e:
		logging.error(e)
	except Exception as e:
		logging.error(e)
	
	
def chooseFilter(update, context, link):
	userid = update.message.from_user.id
	username = update.message.from_user.first_name
	
	obj = PixivObject(link)
	info = obj.setLinkInfo()
	if "furrynovel.com" in link:
		link = getOriginalLink(link)
	
	if "user" in link:
		photo = obj.obj.saveAuthorIcon()
		try:
			update.message.chat.send_photo(open(photo, 'rb'), info, reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("下载全部", callback_data=f"{5}:{obj.author_url}"),
					# InlineKeyboardButton("精确下载", callback_data=f"{6}:{obj.author_url}"),
				]]))
		except IOError as e:
			logging.info(f"未能下载作者头像\n{e}")
			update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("下载全部", callback_data=f"{5}:{obj.author_url}"),
					# InlineKeyboardButton("精确下载", callback_data=f"{6}:{obj.author_url}"),
				]]))
	
	elif "novel/series" in link:
		update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
			[[
				InlineKeyboardButton("下载为txt合集", callback_data=f"{2}:{obj.series_url}"),
				InlineKeyboardButton("下载为zip合集", callback_data=f"{3}:{obj.series_url}"),
				InlineKeyboardButton("自动选择", callback_data=f"{4}:{obj.series_url}"),
			]]))
		
	elif "novel" in link or "/pn/" in link:
		if not obj.series_id:
			update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("下载本章为txt文件", callback_data=f"{1}:{obj.novel_url}"),
					InlineKeyboardButton("下载作者全部小说", callback_data=f"{5}:{obj.author_url}"),
				]]))
		
		else:
			update.message.reply_text(info, reply_markup=InlineKeyboardMarkup(
				[[
					InlineKeyboardButton("下载本章为txt文件", callback_data=f"{1}:{obj.novel_url}"),
					InlineKeyboardButton("下载作者全部小说", callback_data=f"{5}:{obj.author_url}"),
				], [
					InlineKeyboardButton("下载系列为txt合集", callback_data=f"{2}:{obj.series_url}"),
					InlineKeyboardButton("下载系列为zip合集", callback_data=f"{3}:{obj.series_url}")
				]]))
	
	elif "artwork" in link:
		downIllust(update, context)
		return ConversationHandler.END
	else:
		myprint(update, "输入有误，请重新输入")
		return ConversationHandler.END
		
		
def pixivFilters(update: Update, context: ContextTypes):
	try:
		chooseFilter(update, context, getLink(update))
	except TypeError as e:
		logging.debug(f"无链接{e}")
	except ValueError as e:
		myprint(update, e)
		return ConversationHandler.END
	except RuntimeError as e:
		myprint(update, e)
		return ConversationHandler.END
	return SAVEPIXIV


def savePixiv(update: Update, context: ContextTypes):
	def myprint(*args):
		for arg in args:
			try:
				query.message.edit_text(str(arg))  # 修改文字消息
			except telegram.error.BadRequest:
				query.message.edit_caption(str(arg))  # 修改图片 caption
			except Exception as e:
				logging.error(e)
			finally:
				logging.info(str(arg))
				print(arg)
	
	
	@timer
	def uploadToUser(path, info):
		print(f"UploadTo: {username} ({userid})")
		logging.info(f"UploadTo: {username} ({userid})")
		query.message.chat.send_document(open(path, 'rb'), os.path.basename(path), info)
	
	
	@timer
	def uploadToChannel(channel, path, info):
		print(f"上传至频道：{channel}")
		logging.info(f"上传至频道：{channel}")
		context.bot.send_document(channel, open(path, 'rb'), os.path.basename(path), info)
	
	
	def sendMsg(channel, message):
		context.bot.send_message(channel, message, parse_mode="HTML")
	
	
	def deleteMsg(query: update.callback_query):
		try:
			chatid = query.message.chat.id
			context.bot.delete_message(chatid, query.message.message_id)
			if query.message.reply_to_message:
				context.bot.delete_message(chatid, query.message.reply_to_message.message_id)
		except telegram.error.BadRequest as e:
			logging.error(e)
		except Exception as e:
			logging.error(e)
	
	
	def saveNovels(query: update.callback_query):
		method, url = int(query.data[0]), query.data[2:]
		obj = PixivObject(url)
		if method == 1:
			myprint("正在下载当前章节……")
			result = obj.saveNovel(lang2=language)
		elif method == 2:
			myprint("正在下载txt合集中……")
			result = obj.saveSeriesAsTxt(lang2=language)
		elif method == 3:
			myprint("正在下载zip合集中……")
			result = obj.saveSeriesAsZip(lang2=language)
		elif method == 4:
			myprint("正在下载合集中……")
			result = obj.saveSeries(lang2=language)
		elif method == 5:
			myprint("正在下载此作者全部小说……")
			result = obj.saveAuthor(lang2=language)
		elif method == 7:
			myprint("正在下载此作者全部小说……")
			result = obj.saveAuthor(lang2=language)
		else:
			return
		myprint("下载完成，等待上传中……")
		return result, (obj.file_info, obj.trans_info), obj.score, obj.furry, (obj.author_id, obj.author_name)
	
	
	def sendFileToUser(path1, path2, info1, info2):
		print("上传文件路径：", path1, path2, sep="\n")
		logging.info(f"上传文件路径：\n{path1}\n{path2}")
		myprint("还请去Pixiv，给作者一个收藏/评论，以表支持")
		uploadToUser(path1, info1)
		if path2:
			uploadToUser(path2, info2)
	
	
	def setUpdateLog(info1, info2, username, score):
		info = f"{info1}\n\n来自 {username} 的分享\n"  # info 后半部分
		if score > -100:
			info += f"推荐指数： {score} (仅供参考)\n"
		info += f"喜欢还请去Pixiv收藏或评论，以支持作者 @FurryReading"
		info2 = info.replace(info1, info2)
		
		infolist = info1.split("\n")  # logs
		log = f" <a href='tg://user?id={userid}'>{username}</a> #U{userid}\n{infolist[0]}\n{infolist[1]}\n{infolist[2]}"
		if infolist[2] != infolist[-1]:
			log += f"\n{infolist[-1]}"
		return info, info2, log
	
	
	def checkLimited(author_id):
		limited_authors_ids = []
		for author in readJson(r"./data/limited_authors.json"):
			limited_authors_ids.append(author["id"])
		if str(author_id) in limited_authors_ids:
			return True
		else:
			return False
		
	
	def sendFileToChannels(path1, info, path2, info2, score, furry):
		if testMode:  # 测试用
			uploadToChannel(TEST_CHANNEL, path1, info)
			if path2:
				uploadToChannel(TEST_CHANNEL, path2, info2)
		
		elif furry >= 2 and ".zip" not in path1:  # 兽人小说 txt
			uploadToChannel("@FurryNovels", path1, info)
			if path2:  # 上传翻译文件
				uploadToChannel("@FurryNovels", path2, info2)
			
			if "zh" in info and score >= 6:  # 中文优秀非机翻小说
				uploadToChannel("@FurryReading", path1, info)
				uploadToWebdav(path1, "小说")
				uploadToWebSite(info)   # 上传至 www.novel.com
				
			if "#Transfur" in info:  # 中文优秀非机翻小说
				uploadToChannel("@TransfurNovels", path1, info)
				if path2:  # 上传翻译文件
					uploadToChannel("@TransfurNovels", path2, info2)
				
	
	def sendLogToChannels(path1, furry, log):
		if furry >= 2 and ".zip" in path1:  # 兽人小说 zip
			sendMsg(TEST_CHANNEL, f"#兽人小说 {log}")
		elif furry >= 2 and ".txt" in path1:  # 兽人小说 txt
			sendMsg(TEST_CHANNEL, f"#兽人小说 {log}")
		elif ".zip" in path1:  # 作者合集 zip
			sendMsg(TEST_CHANNEL, f"#作者合集 {log}")
		else:  # 非兽人小说
			sendMsg(TEST_CHANNEL, f"#非兽人小说 {log}")
	
	
	@timer
	def uploadNovels(query: update.callback_query):
		try:
			(path1, path2), (info1, info2), score, furry, (author_id, author_name) = saveNovels(query)
		except ValueError as e:
			myprint(e)
			sendMsg(userid, str(e))
			return ConversationHandler.END
		except RuntimeError as e:
			myprint(e)
			sendMsg(userid, str(e))
			return ConversationHandler.END
		else:
			sendFileToUser(path1, path2, info1, info2)
			info, info2, log = setUpdateLog(info1, info2, username, score)
			if not checkLimited(author_id): # 未被限制的小说
				sendFileToChannels(path1, info, path2, info2, score, furry)
			else:
				sendMsg(userid, f"不好意思，作者 {author_name} 已禁止向本频道分享其作品，本次下载的内容将不会分享至 @FurryReading 以及 @FurryNovels")
				log = f"#作者已限制 {log}"
			sendLogToChannels(path1, furry, log)
	
	
	query = update.callback_query
	userid = query.message.chat.id
	username = query.from_user.first_name
	language = query.from_user.language_code
	if "zh-hans" in language:
		language = "zh_cn"
	elif "zh-hant" in language:
		language = "zh_tw"
	print(f"当前语言：{language}")
	logging.info(f"当前语言：{language}")
	if query.data != "":  # 清除按钮
		query.edit_message_reply_markup(InlineKeyboardMarkup([[]]))
	
	try:
		uploadNovels(query)
		time.sleep(3)
		deleteMsg(query)
	except Exception as e:
		myprint(str(e))
	return ConversationHandler.END





def timeoutcb(update: Update, context: ContextTypes):
	# print(f"Conversation timed out: uid={context.user_data['uid']}")
	context.user_data.clear()
	# return ConversationHandler.END


def translateFile(update: Update, context: ContextTypes):
	try:
		chatid = update.message.chat.id
		userid = update.message.from_user.id
		username = update.message.from_user.first_name
		msg = update.message.text
		message, lang2, file, name, caption, path = "", "", "", "", "", ""
	except AttributeError:  # 'NoneType' object has no attribute 'chat'
		return
	
	
	def getLang2(update: Update, context: ContextTypes):
		nonlocal userid, username, chatid, message, lang2
		try:
			message = f"请求者：<a href='tg://user?id={userid}'>{username}</a> #UID{userid}\n"
			text = update.message.text
		except AttributeError:  # 'NoneType' object has no attribute 'chat'
			# print(f"transFile: 长时间闲置，结束翻译")
			# pass
			return ""
		else:
			if text:  # 当前消息指定语言，回复消息指定文件
				text = text.lower().strip().replace("/translate", "").replace("/push", "")
				lang2 = text.replace("-", "_").strip()
			if not lang2:
				lang2 = update.message.from_user.language_code
			if "zh-hans" in lang2:
				lang2 = "zh_cn"
			elif "zh-hant" in lang2:
				lang2 = "zh_tw"
		return lang2
	
	
	def getFile(update: Update, context: ContextTypes):
		nonlocal file, name, caption, message
		if update.message.document:  # 直接上传文件
			file = context.bot.get_file(update.message.document.file_id)
			name = update.message.document.file_name
			caption = update.message.caption
		elif update.message.reply_to_message and update.message.reply_to_message.document:  # 回复文件
			file = context.bot.get_file(update.message.reply_to_message.document.file_id)
			name = update.message.reply_to_message.document.file_name
			caption = update.message.reply_to_message.caption
		else:
			update.message.reply_text(
				text="请直接发送文件或用<code> /translate zh_cn </code>回复文件所在消息",
				reply_to_message_id=update.message.message_id, parse_mode="HTML")
			print(f"transFile: {username} 未发送或回复文件，结束翻译")
			logging.info(f"transFile: {username} 未发送或回复文件，结束翻译")
		return file, name, caption
	
	
	def saveFile(update: Update, context: ContextTypes):
		nonlocal file, name, caption, message, path, caption
		# file, name, caption = getFile(update, context)
		extname = os.path.splitext(name)[1].replace(".", "")
		path = os.path.join(os.getcwd(), "Translation", "Download", name)
		message = f"#{extname}_{lang2} {name}\n{message}"
		
		try:
			makeFile(path, "")  # 保存空文件后再覆盖
			file.download(custom_path=path)
			return path
		except Exception as e:
			update.message.reply_text(f"文件下载错误")
			message = f"#下载错误 {message}\n{e}"
			logging.error(e)
			if testMode:  # 测试用
				message = f"#测试 {message}"
			context.bot.send_message(TEST_CHANNEL, message, parse_mode="HTML")
			print(f"transFile: 下载错误，结束翻译")
			logging.info(f"transFile: 下载错误，结束翻译")
			return
	
	
	def translate(update: Update, context: ContextTypes):
		nonlocal path, caption, lang2, message
		try:
			print(f"transFile: 正在将 {name} 翻译成 {lang2} ")
			logging.info(f"transFile: 正在将 {name} 翻译成 {lang2} ")
			path = transFile(path, lang2)
			if caption:
				caption, lang1 = translateText(caption, lang2=lang2, mode=1)
				caption = caption.replace(lang1, lang2)
		except RuntimeError:
			update.message.reply_text(
			text=f"该文件已与你当前所用语言一致，故未翻译。如需翻译 <a href='https://t.me/TNTwwxs/337'>请更换你的 Telegram 语言包</a>， 或使用 <code>/translate 语言代码</code>", parse_mode="HTML")
			message = f"#无需翻译 {message}"
		except AttributeError:
			update.message.reply_text(f"无法打开当前类型的文件\n仅支持 txt 和 docx 文件")
			message = f"#无法翻译 {message}"
		except Exception as e:
			update.message.reply_text(f"出现未知错误，已向管理发送错误信息")
			message = f"#翻译错误 {message}\n{e}"
			logging.error(e)
		else:
			context.bot.send_document(chatid, open(path, 'rb'), os.path.basename(path), caption)
			if "zh" in lang2:
				uploadToWebdav(path, "翻译")
			message = f"#已经翻译 {message}"
			print(f"翻译完成：{path}")
			logging.info(f"翻译完成：{path}")
		finally:
			if testMode:  # 测试用
				message = f"#测试 {message}"
			context.bot.send_message(TEST_CHANNEL, message, parse_mode="HTML")
	
	
	def pushFile(update, context):
		nonlocal path, caption, lang2, message
		name = os.path.basename(path)
		try:
			print(f"pushFile: 正在获取 {name} 的标签信息")
			logging.info(f"pushFile: 正在获取 {name} 的标签信息")
			caption = printInfo(path)[0]
			# print(caption)
		except Exception as e:
			update.message.reply_text(f"出现未知错误，已向管理发送错误信息")
			message = f"#翻译错误 {message}\n{e}"
			logging.error(e)
		else:
			context.bot.send_document(chatid, open(path, 'rb'), os.path.basename(path), caption)
			message = f"#获取小说信息 {message}\n{caption}"
			print(f"完成获取信息：{path}")
			logging.info(f"完成获取信息：{path}")
		finally:
			if testMode:  # 测试用
				message = f"#测试 {message}"
			context.bot.send_message(TEST_CHANNEL, message, parse_mode="HTML")
	
	
	def transMain(update: Update, context: ContextTypes):
		nonlocal lang2, msg
		lang2 = getLang2(update, context)
		file = getFile(update, context)[0]
		# print(f"{lang2=}\n{file=}")
		if file:
			path = saveFile(update, context)
			translate(update, context)
		if "/push" in msg:
			pushFile(update, context)
			
	
	transMain(update, context)


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
			port=8080,
			url_path=BOT_TOKEN,
			webhook_url=f"{WEB_HOOK}/{BOT_TOKEN}")
	
	updater.dispatcher.add_handler(CommandHandler("start", start))
	updater.dispatcher.add_handler(CommandHandler("help", help))
	updater.dispatcher.add_handler(CommandHandler("ping", ping))
	updater.dispatcher.add_handler(CommandHandler("cancel", cancel))
	updater.dispatcher.add_handler(CommandHandler("source", source))
	updater.dispatcher.add_handler(CommandHandler("delete", deleteFolders))
	updater.dispatcher.add_handler(CommandHandler("translate", translateFile))
	updater.dispatcher.add_handler(CommandHandler("push", translateFile))
	updater.dispatcher.add_handler(CommandHandler("novellist", downNovelsList))
	updater.dispatcher.add_handler(MessageHandler(Filters.document, translateFile))
	updater.dispatcher.add_handler(MessageHandler(Filters.regex('(artworks).+[0-9]{5,}'), downIllust))
	updater.dispatcher.add_handler(InlineQueryHandler(inlineIllust))
	
	
	updater.dispatcher.add_handler(ConversationHandler(
		entry_points=[
			CommandHandler("download", pixivFilters),
			MessageHandler(Filters.regex('(pixiv|pn|furrynovel).+[0-9]{1,}'), pixivFilters),
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
	
	updater.dispatcher.add_error_handler(error)
	updater.idle()


if __name__ == '__main__':
	REQUESTS_KWARGS = {'proxy_url': proxy_list[0]}
	try:
		print(f"Bot is Running! {datetime.now()}")
		# logging.info(f"Bot is Running! {datetime.now()}")
		main()
	except telegram.error.NetworkError as e:
		logging.warning(e)
		logging.info("Error")
