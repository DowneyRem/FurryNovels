#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 正文种族，职业对应标签
# 适用于文本的标签关键词
# key为关键词，value为对应标签
# 关键词——标签可以一对多


def makeRaceDict():
	prefix = "赤 红 橙 黄 绿 青 蓝 紫 黑 白 灰 棕 粉 大 小 胶".split(" ")
	suffix = "兽人 兽 人 族 角 头 吻 身 爪 脚 尾".split(" ")
	r18suffix = "棒 根 穴".split(" ")
	races = {
		"熊": "bear",
		"熊猫": "panda",
		"马": "horse",
		"牛": "bull",
		"犀牛": "rhinoceros",
		"羊": "sheep",
		"猫": "cat",
		"狮": "lion",
		"狮子": "lion",
		"虎": "tiger",
		"龙": "dragon",
		"蜥蜴": "lizard",
		"狗": "dog",
		"狼": "wolf",
		"狐": "fox",
		"狐狸": "fox",
		"鲨狗": "sergal",
		"鯊格魯": "sergal",
		"鱼": "fish",
		"鲨": "shark",
		"鲨鱼": "shark",
		"鳄鱼": "crocodile",
		"海豚": "dolphin",
		"象": "elephant",
		"鼠": "mouse",
		"袋鼠": "kangaroo",
		"猴": "monkey",
		"豹": "panther",
		"猪": "pig",
		"兔": "rabbit",
		"蛇": "snake",
		"龟": "turtle",
		"鸟": "harpy",
		"胶": "rubber",
		}
	
	others = {
		"兽族": "furry",
		"兽人": "furry",
		"兽兽": "furry",
		# "纯兽": "non-anthro",
		}
	
	for i in races:
		for j in prefix:  # 添加前缀
			racedict[j+i] = [races[i].capitalize()]
		for j in suffix:  # 添加后缀
			racedict[i+j] = [races[i].capitalize()]
		for j in r18suffix:  # 添加后缀
			racedict[i+j] = [races[i].capitalize(), "R18"]
	for i in others:
		racedict[i] = [others[i].capitalize()]
	
	racelist.extend(list(races.values()))
	racelist.extend(list(others.values()))
	
	
racedict = {}
racelist = []
makeRaceDict()


if __name__ == '__main__':
	# print(racedict)
	print(racelist)
	pass
