#!/usr/bin/python
# -*- coding: UTF-8 -*-
from nonebot import on_command, CommandSession
from .TencentQQBot import *


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