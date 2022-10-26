#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

from .PixivClass import getUrl, PixivObject
from .FileOperate import zipFile, removeFile
from .Webdav4 import uploadAll as uploadWebdav
from .configuration import novel_path, password


download_help = """
⬇️FFF下载功能帮助
下列文字指令同样支持繁体中文；群内下载后会自动加密，密码：furry；请使用支持 AES256 的解压软件解压

0️⃣根据链接自行下载
【FFF 下载 + 网址】

1️⃣指定方法下载
⏺下载单篇小说
【FFF 下载 小说 + 网址】
⏺下载系列合集
【FFF 下载 系列 + 网址】
⏺指定下载作者合集
【FFF 下载 作者 + 网址】

2️⃣指定格式下载
⏺下载系列为txt合集
【FFF 下载 系列 txt + 网址】
⏺下载系列为zip合集
【FFF 下载 系列 zip + 网址】

3️⃣帮助 & 其他：
⏺查看下载指令【下载帮助】
【FFF 下载 帮助/命令/指令】
⏺查看源代码等
【FFF 开发者/赞助/其他】
""".strip()

credits = """
开发：@唐尼瑞姆 DowneyRem
协助：@upanther, @eatswap, @windyhusky

Github：https://github.com/DowneyRem/FurryNovels/tree/main/TencentQQBot
Pixiv：https://www.pixiv.net/users/16721009
爱发电：https://afdian.net/@TNTwwxs

ＱＱ机器人：@FFF
电报机器人：https://t.me/FurryNovelsBot
兽人小说频道：https://t.me/FurryNovels
""".strip()

async def filter(text, link, lang="zh_cn"):
	obj = PixivObject(link)
	# print(f"{text=}")
	if "单章" in text or "小说" in text or "小説" in text:
		path1, path2 = obj.saveNovel(lang)
	elif "系列" in text:
		# elif "系列" in text or obj.series_id:
		if "zip" in text:
			path1, path2 = obj.saveSeriesAsZip(lang)
		elif "txt" in text:
			path1, path2 = obj.saveSeriesAsTxt(lang)
		else:
			path1, path2 = obj.saveSeries(lang)
	elif "作者" in text:
		path1, path2 = obj.saveAuthor(lang)
	else:
		path1, path2 = obj.save(lang)
	score, furry = obj.score, obj.furry
	return path1, path2, score, furry


async def download(session, text, link, lang):
	try:
		print(f"正在下载：{link}")
		path1, path2, score, furry = await filter(text, link, lang)
	except ValueError as e:
		await session.send(str(e))
		return
	else:
		await upload(session, path1, path2, score, furry)


async def upload(session, path1, path2, score, furry):
	if session.ctx.message_type == "private":
		await session.bot.upload_private_file(user_id=session.ctx.user_id, file=path1, name=os.path.basename(path1))
		if os.path.exists(path2):
			await session.bot.upload_private_file(
				user_id=session.ctx.user_id, file=path1, name=os.path.basename(path2))
	
	elif session.ctx.message_type == "group":
		zippath1, zippath2 = "", ""
		zipfolder = os.path.join(novel_path, "ZipFiles")
		
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
			await session.send("密码：【furry】，请使用支持 AES256 加密的解压软件解压")
		removeFile(zipfolder)
	
	if not path2 and ".zip" not in path1 and furry >= 2 and score >= 6:
		uploadWebdav(path1, "QQ")
