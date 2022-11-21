# #!/usr/bin/python
# # -*- coding: UTF-8 -*-
import time
import random

from nonebot import on_command, CommandSession
from nonebot import on_request, RequestSession
from nonebot import on_notice, NoticeSession
from nonebot.permission import PRIVATE_FRIEND
from config import NICKNAME, SUPERUSERS


__plugin_name__ = "好友"
__plugin_usage__ = """
▶️ 检测是否为双向好友
⚠️ 不应该在加好友之前发送
""".strip()


nickname = NICKNAME[0].upper()
friend_message = [
	f"你已经是{nickname}的好友了，",
	f"{nickname}已经是你的好友了，",
	f"欢迎使用{nickname}，",
	f"你好，这里是{nickname}，",
	f"你好，我是机械龙{nickname}，",
	f"我是{nickname}，唐门主龙的机械龙，",
	f"机械龙{nickname}，在此向您服务，",
	]
help_message = [
	f"查看帮助可以发送【帮助】哦",
	f"可以发送【帮助】查看帮助哦",
	f"想要了解更多{nickname}的功能，可以发送【帮助】",
	f"快发送【帮助】来使用{nickname}吧",
	f"可以发送【帮助】，了解更多{nickname}的功能哦"
]


@on_command("check", aliases=("好友检测", "检测好友", "好友"), permission=PRIVATE_FRIEND)
async def checkFriends(session: CommandSession):
	is_friend = None
	user_id = session.ctx.user_id
	friends = await session.bot.get_friend_list()
	for friend in friends:
		if user_id == friend["user_id"]:
			is_friend = True
			
	if is_friend:
		message = f"{random.choice(friend_message)}{random.choice(help_message)}"
		time.sleep(random.uniform(1, 5))
		await session.send(f"{message}", at_sender=True)
	else:
		await session.send("我们还不是好友哦", at_sender=True)


@on_request("friend")
async def acceptFriendRequest(session: RequestSession):
	time.sleep(random.uniform(1, 10))
	await session.approve()
	time.sleep(random.uniform(1, 5))
	message = f"{random.choice(friend_message)}{random.choice(help_message)}"
	await session.send(message)


@on_request('group')
async def acceptGroupRequest(session: RequestSession):
	if session.event.sub_type == "invite":  # 邀请机器人进群
		if session.event.user_id in SUPERUSERS:  # 管理员邀请，直接同意
			time.sleep(random.uniform(1, 10))
			await session.approve()
			
		else:  # 非管理员邀请
			user_id = session.event.user_id
			resp = await session.bot.get_stranger_info(user_id=user_id)
			user_name = resp["nickname"]
			
			group_id = session.event.group_id
			resp = await session.bot.get_group_info(group_id=group_id)
			group_name = resp["group_name"]
			
			time.sleep(random.uniform(1, 5))
			await session.bot.send_msg(
				user_id=SUPERUSERS[0],
				message=f"{user_name}({user_id})，邀请{nickname}加入【{group_name}】({group_id})")
		return
	
	# if session.event.sub_type == "add":  # 别人主动加群
	# 	if '暗号' in session.event.comment:
	# 		# 验证信息正确，同意入群
	# 		await session.approve()
	# 		return
	# # await session.reject('请说暗号')


# @on_command("welcome", aliases=("欢迎",), only_to_me=False)
# async def checkFriends(session: CommandSession):
# 	time.sleep(random.uniform(1, 5))
# 	await session.send(welcome_message)


@on_notice("group_increase")
async def groupIncrease(session: NoticeSession):
	user_id = session.event.user_id
	resp = await session.bot.get_stranger_info(user_id=user_id)
	user_name = resp["nickname"]
	
	group_id = session.event.group_id
	resp = await session.bot.get_group_info(group_id=group_id)
	group_name = resp["group_name"]
	
	time.sleep(random.uniform(1, 5))
	await session.bot.send_msg(
		group_id=group_id,
		message=f"欢迎{user_name}来到{group_name}")


@on_notice("group_decrease")
async def groupDecrease(session: NoticeSession):
	user_id = session.event.user_id
	resp = await session.bot.get_stranger_info(user_id=user_id)
	user_name = resp["nickname"]
	
	operator_id = session.event.operator_id
	resp = await session.bot.get_stranger_info(user_id=user_id)
	operator_name = resp["nickname"]
	
	group_id = session.event.group_id
	resp = await session.bot.get_group_info(group_id=group_id)
	group_name = resp["group_name"]
	
	if session.event.sub_type == "kick_me":  # bot被踢
		time.sleep(random.uniform(1, 5))
		await session.bot.send_msg(
			user_id=SUPERUSERS[0],
			message=f"{nickname}被{operator_name}({operator_id})踢出了{group_name}({group_id})")
	
	# elif session.event.sub_type == "kick":  # 别人被踢
	# 	time.sleep(random.uniform(1, 5))
	# 	await session.bot.send_msg(
	# 		user_id=SUPERUSERS[0],
	# 		message=f"{user_name}({user_id})被{operator_name}({operator_id})踢出了{group_name}({group_id})")
	#
	# # elif session.event.sub_type == "leave":  # 别人退群
	# else:
	# 	time.sleep(random.uniform(1, 5))
	# 	await session.bot.send_msg(group_id=group_id, message=f"{user_name}({user_id}) 离开了我们。")
