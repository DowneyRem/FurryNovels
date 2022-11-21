#!/usr/bin/python
# -*- coding: UTF-8 -*-
from nonebot import on_command, CommandSession
from config import NICKNAME


nickname = NICKNAME[0]
translate_help = f"""
🌐 翻译功能帮助
1️⃣ 加{nickname}为好友
2️⃣ 私聊发送小说文件
3️⃣ 无需发送【翻译】二字

⚠️ 目前仅支持翻译成简体中文
⚠️ 仅支持 txt 和 docx 文档
⚠️ 仅支持 zip 压缩文件中的 docx 和 txt 文档
""".strip()


__plugin_name__ = "翻译"
__plugin_usage__ = translate_help


@on_command("translate", aliases=("翻译", "翻译帮助", "翻譯", "翻譯幫助"), only_to_me=False)
async def translateHelp(session: CommandSession):
	is_friend = None
	friends = await session.bot.get_friend_list()
	for friend in friends:
		if session.ctx.user_id == friend["user_id"]:
			is_friend = True
			
	if not is_friend:
		await session.send("快加我为好友吧。加了好友才能【接收文件】开始翻译哦")
		return
	await session.send(translate_help)
