#!/usr/bin/python
# -*- coding: UTF-8 -*-
from nonebot import on_command, CommandSession

from .PixivClass import getUrl
from .TencentQQBot import download


# on_command 装饰器将函数声明为一个命令处理器
@on_command("down", aliases=("下载", "下载小说"))
# @on_command("down", aliases=("下载", "下载小说"), only_to_me=False)
async def down(session: CommandSession):
	text = session.current_arg_text.strip()
	if "帮助" in text or "命令" in text or "指令" in text:
		await session.send(download_help)
		return
	
	link = getUrl(text)
	while not link:  # 如果用户只发送空白符，则继续询问
		text = (await session.aget(prompt="请发送 Pixiv 或 Linpx 的小说链接，发送“退出”退出下载")).strip()  # 更新 text
		if "退出" in text:
			await session.send("已退出下载")
			return
		else:
			link = getUrl(text)
	await download(session, text, link, "zh_cn")
	
	
@on_command("down2", aliases=("下載", "下載小説"))
async def down2(session: CommandSession):
	text = session.current_arg_text.strip()
	if "幫助" in text or "命令" in text or "指令" in text:
		await session.send(download_help)
		return
	
	link = getUrl(text)
	while not link:  # 如果用户只发送空白符，则继续询问
		text = (await session.aget(prompt="請發送 Pixiv 或 Linpx 的小説鏈接，發送“退出”退出下載")).strip()
		if "退出" in text:
			await session.send("已退出下載")
			return
		else:
			link = getUrl(text)
	await download(session, text, link, "zh_tw")


@on_command("down3", aliases=("下载帮助", "下載幫助"), only_to_me=False)
async def down3(session: CommandSession):
	await session.send(download_help)
	
	
@on_command("down4", aliases=("开发者", "赞助", "其他", "開發者", "贊助"), only_to_me=False)
async def down4(session: CommandSession):
	await session.send(credits)
	
	
download_help = """
⬇️FFF下载功能帮助
下列文字指令同样支持繁体中文；
群内下载后会自动加密，密码：furry，请使用支持 AES256 加密方式的解压软件解压；
所有下载的 txt 兽人小说 均会转发到TG频道 @FurryReading ，作为你的分享

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
