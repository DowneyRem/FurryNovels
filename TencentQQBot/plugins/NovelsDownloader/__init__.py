#!/usr/bin/python
# -*- coding: UTF-8 -*-
from nonebot import on_command, CommandSession, SenderRoles, permission
from nonebot import on_notice, NoticeSession

from .PixivClass import getUrl
from .TencentQQBot import download, deleteFolders, translate
from .configuration import password


@on_command("down1", aliases=("下载", "下載"), patterns="[下载,下載]+.[pixiv, /pn/]+.[0-9]{5,}", only_to_me=False)
async def down1(session: CommandSession):
	text = session.current_arg_text.strip()
	if "帮助" in text or "幫助" in text or "示例" in text:
		await session.send(down_help)
		return
	
	link = getUrl(text)
	while not link:  # 如果用户只发送空白符，则继续询问
		text = (await session.aget(prompt=quit_message)).strip()  # 更新 text
		if "退出" in text:
			await session.send("已退出下载")
			return
		else:
			link = getUrl(text)
	await download(session, text, link)
	
	
@on_command("down2", patterns="[pixiv, /pn/].+[0-9]{5,}", permission=permission.PRIVATE_FRIEND)
async def down2(session: CommandSession):
	text = session.current_arg_text.strip()
	link = getUrl(text)
	if link:
		await download(session, text, link)


@on_command("downHelp", aliases=("下载帮助", "下載幫助", "下载示例", "下載示例"), only_to_me=False)
async def downHelp(session: CommandSession):
	await session.send(down_help)


def admin_permission(sender: SenderRoles):
	return sender.is_superuser or sender.is_owner or sender.is_admin


@on_command("delete", aliases=("下载删除", "删除下载", "删除小说"), permission=admin_permission)
async def delete(session: CommandSession):
	await deleteFolders(session)


@on_notice("offline_file")
async def translator(session: NoticeSession):
	lang2 = ""  # 读取设置的语言？
	if lang2:
		await translate(session, lang2)
	else:
		await translate(session, "zh_cn")


down_help = f"""
⬇️ 下载帮助：
下面用「链接」代指【维卡斯】的长篇系列小说【龙族陷落第一部】的第一章【龙族陷落序章】的链接：
https://www.pixiv.net/novel/show.php?id=11878466
🉑 下载 Pixiv 或 Linpx 的小说/系列/作者链接

🉑 下载链接对应内容
【链接】或【下载 链接】

🉑 批量下载(无需修改链接)
1️⃣ 下载【序章】这一单篇
【下载 小说 链接】

2️⃣ 下载【龙族陷落】系列合集
▶️ 自动选择下载格式
【下载 系列 链接】
▶️ 下载成 txt 合集
【下载 系列 txt 链接】
▶️ 下载成 zip 合集
【下载 系列 zip 链接】

3️⃣ 下载【维卡斯】全部小说
【下载 作者 链接】

⚠️ 【下载 小说/系列/作者 链接】三者以空格间隔；
⚠️ 群内下载的文件会自动加密，密码：{password}，请使用支持 AES256 解压软件，如 ZArchiver 解压；
⚠️ 所有下载的 txt 兽人小说 均会转发到TG频道 @FurryReading ，作为你的分享
""".strip()


__plugin_name__ = "下载"
__plugin_usage__ = down_help
quit_message = "请发送 Pixiv 或 Linpx 的小说链接，发送【退出】退出下载"
