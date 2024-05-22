#!/usr/bin/python
# -*- coding: UTF-8 -*-
import nonebot
from nonebot import on_command, CommandSession
from config import NICKNAME

nickname = NICKNAME[0]
__plugin_name__ = "帮助"
__plugin_usage__ = f"""
你在做什么奇怪的事情？[CQ:face,id=178]

【】括号内的文字都是「指令」
私聊可以直接向我发送「指令」
群内可以 @我 后发送「指令」
或直接发送「{nickname} 指令」
""".strip()


@on_command('usage', aliases=['帮助', '命令', '指令', '使用帮助', '使用方法'], only_to_me=False)
async def usage(session: CommandSession):
	# 获取设置了名称的插件列表
	plugins = list(filter(lambda p: p.name, nonebot.get_loaded_plugins()))

	arg = session.current_arg_text.strip().lower()
	if not arg:  # 如果用户没有发送参数，则发送功能列表
		await session.send(help_message)
		# await session.send(
		# 	'我现在支持的功能：\n【' +
		# 	'】\n【'.join(p.name for p in plugins) + '】\n')
		return

	for p in plugins:  # 发送对应功能的帮助
		if p.name.lower() in arg.strip().lower():
			await session.send(p.usage)
			
			
@on_command("credit", aliases=("开发者", "赞助", "其他", "開發者", "贊助"), only_to_me=False)
async def credit_msg(session: CommandSession):
	await session.send(about_message)
	
	
help_message = f"""
—— {nickname} 指令一览表 ——
👤 好友可用 | 👥 群内可用
❌ 不可使用 | 📝 功能开发中

👤👥【下载】下载小说
👤❌【翻译】翻译小说

👤👥【开发者/赞助】源代码等
👤👥【帮助】查看指令(本表)
👤👥【帮助 「指令」】
查看具体 「指令」的帮助内容

【】括号内的文字都是「指令」
私聊可以直接向我发送「指令」
群内可以 @我 后发送「指令」
或直接发送「{nickname} 指令」
""".strip()

"""
👤❌【好友】检测双向好友
👤❌【互动】互动剧情
"""

about_message = f"""
开发：@唐尼瑞姆 DowneyRem
协助：@upanther, @eatswap, @windyhusky

Github：https://github.com/DowneyRem/FurryNovels/tree/main/TencentQQBot
Pixiv：https://www.pixiv.net/users/16721009
爱发电：https://afdian.net/@TNTwwxs

ＱＱ机器人：@{nickname}
电报机器人：https://t.me/FurryNovelsBot
兽人小说频道：https://t.me/FurryNovels
""".strip()
