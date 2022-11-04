#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from platform import platform

from .PixivClass import PixivObject
from .FileOperate import zipFile, removeFile
from .TelegramBot import sendMsgToChannel, uploadToChannel
from .Webdav4 import uploadAll as uploadWebdav
from .configuration import novel_path, password


async def filter(text, link, lang="zh_cn"):
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


async def uploadToQQ(session, path1, path2):
	if session.ctx.message_type == "private":
		await session.bot.upload_private_file(user_id=session.ctx.user_id, file=path1, name=os.path.basename(path1))
		if os.path.exists(path2):
			await session.bot.upload_private_file(
				user_id=session.ctx.user_id, file=path1, name=os.path.basename(path2))
	
	elif session.ctx.message_type == "group":
		zipfolder = os.path.join(novel_path, "ZipFiles")
		await session.send("密码：【furry】，请使用支持 AES256 加密的解压软件解压")
		
		name1 = os.path.splitext(os.path.basename(path1))[0]
		zippath1 = os.path.join(zipfolder, f"{name1}.zip")
		zipFile(path1, password=password, zippath=zippath1)
		await session.bot.upload_group_file(
			group_id=session.ctx.group_id, file=zippath1, name=f"{name1} (密码：{password}).zip")
		
		if os.path.exists(path2):
			name2 = os.path.splitext(os.path.basename(path2))[0]
			zippath2 = os.path.join(zipfolder, f"{name2}.zip")
			zipFile(path2, password=password, zippath=zippath2)
			await session.bot.upload_group_file(
				group_id=session.ctx.group_id, file=zippath2, name=f"{name2} (密码：{password}).zip")
		removeFile(zipfolder)


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
	
	if "Windows" in platform():  # 测试用
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
	
	
async def download(session, text, link, lang):
	try:
		print(f"正在下载：{link}")
		(path1, path2), (info1, info2), score, furry = await filter(text, link, lang)
	except ValueError as e:
		await session.send(str(e))
		return
	else:
		qqnum = session.ctx.sender["user_id"]
		qname = session.ctx.sender["nickname"]
		await uploadToQQ(session, path1, path2)
		await uploadToTelegram(path1, path2, info1, info2, score, furry, qqnum, qname)
		
		