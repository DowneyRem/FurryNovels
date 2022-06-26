#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 正文种族，职业对应标签
# 适用于文本的标签关键词
# key为关键词，value为对应标签
# 关键词——标签可以一对多


def makeRaceDict():
	color = "赤 红 橙 黄 绿 青 蓝 紫 黑 白 灰 棕 粉".split(" ")
	people = "兽人 兽 人 头 爪 吻 尾".split(" ")
	penis = "棒 根 穴".split(" ")
	race = {
		"熊": "bear",
		"熊猫": "panda",
		"马": "horse",
		"牛": "bull",
		"羊": "sheep",
		"猫": "cat",
		"狮": "lion",
		"狮子": "lion",
		"虎": "tiger",
		"龙": "dragon",
		"蜥蜴": "Lizard",
		"狗": "dog",
		"狼": "wolf",
		"狐狸": "fox",
		"鱼": "fish",
		"鲨鱼": "shark",
		"海豚": "dolphin",
		"象": "elephant",
		"袋鼠": "kangaroo",
		"猴": "monkey",
		"鼠": "mouse",
		"豹": "panther",
		"猪": "pig",
		"兔": "rabbit",
		"犀牛": "rhinoceros",
		"蛇": "snake",
		"龟": "turtle",
		"鲨狗": "Sergal",
		"鳄鱼": "Crocodile",
		"鸟": "Harpy",
		"胶": "Rubber",
		}
	others = {
		"龙兽": "dragon",
		"龙族": "dragon",
		"兽族": "furry",
		"兽人": "furry",
		"兽兽": "furry",
		# "纯兽": "non-anthro",
		"人类": "Human",
		"机器人": "Robot",
		"史莱姆": "Slime",
		"触手": "Tentacles",
		"吸血鬼": "Vampire",
		"人皮服装": "SkinSuit",
		"怪物": "Monster",
		"英雄": "Hero",
		"警察": "Police",
		"特警": "Police",
		"魔王": "DevilKing",
		"恶魔": "Devil",
		"勇者": "Brave",
		"魅魔": "Succubus",
		"医生": "Doctor",
		}
	
	for i in race:
		for j in people:
			racedict[i+j] = [race[i].capitalize()]
		for j in color:
			racedict[j+i] = [race[i].capitalize()]
		for j in penis:
			racedict[i+j] = [race[i].capitalize(), "R18"]
	for i in others:
		racedict[i] = [others[i].capitalize()]
		
		
racedict = {}
makeRaceDict()
if __name__ == '__main__':
	print(racedict)