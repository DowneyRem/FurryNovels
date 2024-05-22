#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

import aiohttp
import aiocqhttp.exceptions
from nonebot import CommandSession, NoticeSession
from config import NICKNAME

from .PixivClass import PixivObject
from .FileOperate import zipFile, removeFile, makeFile
from .TelegramBot import sendMsgToChannel, uploadToChannel
from .Translate import transFile
from .Webdav4 import uploadAll as uploadWebdav
from .configuration import novel_path, password, testMode


nickname = NICKNAME[0]
is_folder_FFF_exists = None


async def downloadFilter(text: str, link: str, lang="zh_cn"):
	obj = PixivObject(link)
	# print(f"{text=}")
	if "单章" in text or "小说" in text or "小説" in text:
		obj.saveNovel(lang)
	elif "系列" in text:
		# elif "系列" in text or obj.series_id:
		if "zip" in text:
			obj.saveSeriesAsZip(lang)
		elif "txt" in text:
			obj.saveSeriesAsTxt(lang)
		else:
			obj.saveSeries(lang)
	elif "作者" in text:
		obj.saveAuthor(lang)
	else:
		obj.save(lang)
	return (obj.file_path, obj.trans_path), (obj.file_info, obj.trans_info), obj.score, obj.furry


async def download(session: CommandSession, text: str, link: str, lang="zh_cn"):
	if "下載" in text or "小説" in text:
		lang = "zh_tw"
	
	try:
		print(f"\n正在下载：{link}")
		(path1, path2), (info1, info2), score, furry = await downloadFilter(text, link, lang)
	except ValueError as e:
		await session.send(str(e))
		return
	except RuntimeError as e:
		await session.send(str(e))
		return
	else:
		qqnum = session.ctx.sender["user_id"]
		qname = session.ctx.sender["nickname"]
		await uploadToQQ(session, path1, path2)
		await uploadToTelegram(path1, path2, info1, info2, score, furry, qqnum, qname)
		print("", "")
		
		
async def createFolder(session: CommandSession):
	try:  # 新建文件夹
		name = f"{nickname}下载 (密码：{password})"
		await session.bot.create_group_file_folder(group_id=session.ctx.group_id, name=name, parent_id="/")
	except aiocqhttp.exceptions.ActionFailed:  # 可以建立，但非常慢，建立后无法上传到文件夹内
		# await session.send(f"群文件没有【{nickname}】文件夹，故上传至根目录。如需自动分类下载文件，请在群文件创建【含有{nickname}】文件夹")
		pass
	
	
async def findFolder(session: CommandSession):
	folder_name, folder_id = "", ""
	is_folder_exists = None
	result = await session.bot.get_group_root_files(group_id=session.ctx.group_id)
	
	try:
		for folder in result["folders"]:
			if nickname.upper() in folder["folder_name"].upper():
				folder_name = folder["folder_name"]
				folder_id = folder["folder_id"]
				print(folder_name)
				is_folder_exists = True
	except TypeError:  # 'NoneType' object is not iterable
		is_folder_exists = False
	
	# await session.send(f"{folder_name}\n{folder_id}")
	# await session.send(f"{is_folder_FFF_exists=}")
	return is_folder_exists, folder_id

	
async def checkFolder(session: CommandSession):
	is_folder_exists, folder_id = await findFolder(session)
	while not is_folder_exists:
		await createFolder(session)
		is_folder_exists, folder_id = await findFolder(session)
		break
	return is_folder_exists, folder_id


async def uploadToQQGroup(session: CommandSession, path1: str, path2: str):
	is_folder_exists, folder = await findFolder(session)
	if not is_folder_exists:
		await session.send(f"如需自动分类下载文件，请在群文件创建【含有{nickname}】的文件夹")
	
	zipfolder = os.path.join(novel_path, "ZipFiles")
	name1 = os.path.splitext(os.path.basename(path1))[0]
	zippath1 = os.path.join(zipfolder, f"{name1}.zip")
	zipFile(path1, password=password, zippath=zippath1)
	await session.bot.upload_group_file(
		group_id=session.ctx.group_id, file=zippath1, name=f"{name1} (密码：{password}).zip", folder=folder)
	
	if os.path.exists(path2):
		name2 = os.path.splitext(os.path.basename(path2))[0]
		zippath2 = os.path.join(zipfolder, f"{name2}.zip")
		zipFile(path2, password=password, zippath=zippath2)
		await session.bot.upload_group_file(
			group_id=session.ctx.group_id, file=zippath2,
			name=f"{name2} (密码：{password}).zip", folder=folder)
	
	await session.send(f"密码：【{password}】，请使用支持 AES256 加密的解压软件解压")
	removeFile(zipfolder)
	

async def uploadToQQ(session: CommandSession, path1: str, path2: str):
	global is_folder_FFF_exists
	if session.ctx.message_type == "private":
		await session.bot.upload_private_file(user_id=session.ctx.user_id, file=path1, name=os.path.basename(path1))
		if os.path.exists(path2):
			await session.bot.upload_private_file(
				user_id=session.ctx.user_id, file=path1, name=os.path.basename(path2))
	
	elif session.ctx.message_type == "group":
		await uploadToQQGroup(session, path1, path2)
		
	else:
		await session.send("请加FFF为好友，或在群内使用")
		

async def uploadToTelegram(path1, path2, info1, info2, score, furry, userid, username):
	info = f"{info1}\n\n来自 {username} 的分享\n"  # info 后半部分
	if score > -100:
		info += f"推荐指数： {score} (仅供参考)\n"
	info += f"喜欢还请去Pixiv收藏或评论，以支持作者 @FurryNovels"
	info2 = info.replace(info1, info2)
	
	infolist = info1.split("\n")  # logs
	log = f"#Q{userid} {username}\n{infolist[0]}\n{infolist[1]}\n{infolist[2]}"
	if infolist[2] != infolist[-1]:
		log += f"\n{infolist[-1]}"
	
	# testMode = 1
	if testMode:  # 测试用
		print("上传文件路径：", path1, path2, sep="\n")
		sendMsgToChannel("TestChannel", f"#测试 {log}")
		uploadToChannel("TestChannel", path1, info)
		if path2:
			uploadToChannel("TestChannel", path2, info2)
		
	elif ".zip" not in path1 and furry >= 2:  # 兽人小说 txt
		sendMsgToChannel("TestChannel", f"#兽人小说 {log}")
		uploadToChannel("@FurryReading", path1, info)
		if path2:
			uploadToChannel("@FurryReading", path2, info2)
		
		if "zh" in info1 and score >= 6:  # 中文优秀非机翻小说
			uploadToChannel("@FurryNovels", path1, info)
			uploadWebdav(path1, "小说")
			
	elif furry >= 2 and ".zip" in path1:  # 兽人小说 zip
		sendMsgToChannel("TestChannel", f"#兽人小说 {log}")
	elif ".zip" in path1:  # 作者合集 zip
		sendMsgToChannel("TestChannel", f"#作者合集 {log}")
	else:  # 非兽人小说
		sendMsgToChannel("TestChannel", f"#非兽人小说 {log}")
		
		
async def deleteFolders(session: CommandSession):
	li = "backup data".split(" ")
	path = os.path.dirname(__file__)
	for folder in os.listdir(path):
		directory = os.path.join(path, folder)
		if os.path.isdir(directory) and not folder.startswith(".") and folder not in li:
			removeFile(directory)
			print(f"已删除：{directory}")
			await session.send(f"已删除：{folder}")
	await session.send("删除完成")


async def downloadFile(url: str, path: str):
	makeFile(path)  # 创建一个空文件
	async with aiohttp.ClientSession() as session:
		async with session.get(url) as resp:
			with open(path, 'wb') as f:
				# iter_chunked() 设置每次保存文件内容大小，单位bytes
				async for chunk in resp.content.iter_chunked(1024):
					f.write(chunk)
	return path


async def translate(session: NoticeSession, lang2: str):
	qqnum = session.ctx.user_id
	result = await session.bot.get_stranger_info(user_id=qqnum)
	qname = result["nickname"]
	message = f"请求者：{qname} #Q{qqnum}"
	
	name, url = session.event.file["name"], session.event.file["url"]
	path = os.path.join(os.path.dirname(__file__), "Translation", name)
	extname = os.path.splitext(path)[1].replace(".", "")
	message = f"#{extname}_{lang2} {name}\n{message}"
	print(f"\ntransFile: 正在将 {name} 翻译成 {lang2} ")
	await downloadFile(url, path)

	try:
		path2 = transFile(path, lang2=lang2)
		name2 = os.path.basename(path2)
	except RuntimeError:
		await session.send(f"该文件已是【简体中文】，故未翻译")
		message = f"#无需翻译 {message}"
	except AttributeError:
		await session.send(f"无法打开当前类型的文件\n仅支持 txt 和 docx 文件")
		message = f"#无法翻译 {message}"
	except Exception as e:
		await session.send(f"出现未知错误，已向管理发送错误信息")
		message = f"#翻译错误 {message}\n{e}"
	else:
		await session.bot.upload_private_file(user_id=qqnum, file=path2, name=name2)
		if "zh" in lang2:
			uploadWebdav(path2, "翻译")
		message = f"#已经翻译 {message}"
		print(f"翻译完成：{path2}\n")
	finally:
		if testMode:  # 测试用
			message = f"#测试 {message}"
		sendMsgToChannel("TestChannel", f"{message}")
