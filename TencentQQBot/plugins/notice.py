#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import random

from nonebot import on_command, CommandSession
from nonebot.permission import SUPERUSER
from config import testMode, black_list, testGroup


@on_command("notice", aliases=("通知", "公告"), permission=SUPERUSER)
async def notice(session: CommandSession):
	notice_groups = {}
	groups = await session.bot.get_group_list()
	for group in groups:
		group_id = group["group_id"]
		group_name = group["group_name"]
		if group_id not in black_list:
			notice_groups[group_id] = group_name
		# print(f'{group["group_id"]} : {group["group_name"]}')
	
	if testMode:
		resp = await session.bot.get_group_info(group_id=testGroup)
		group_name = resp["group_name"]
		notice_groups = {testGroup: group_name}
		
	text = (await session.aget(prompt="请发送要群发的通知内容：")).strip()
	if text:  # 以机器人名字开头时，其名字会被替换为空
		confirm = (await session.aget(prompt="是否发送？")).strip()
		if "是" in confirm or "发送" in confirm:
			for group in notice_groups:
				time.sleep(random.uniform(1, 3))
				await session.bot.send_group_msg(group_id=group, message=text)
				
			group_names = "\n".join(notice_groups.values())
			await session.send(f"上述内容已经发送到下列{len(notice_groups)}个群中：\n{group_names}")
		else:
			await session.send(f"取消发送")
			return
		
		