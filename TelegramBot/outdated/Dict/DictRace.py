#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 正文种族，职业对应标签
# 适用于文本的标签关键词
# key为关键词，value为对应标签，
# 关键词——标签可以一对多

racedict = {
	"熊兽人": "bear",
	"熊猫兽人": "panda",
	"熊猫": "panda",
	"马兽人": "hourse",
	"牛兽人": "bull",
	"羊兽人": "sheep",
	"猫兽人": "cat",
	"狮兽人": "lion",
	"狮子兽人": "lion",
	"虎兽人": "tiger",
	"虎人": "tiger",
	"龙": "dragon",
	"龙兽": "dragon",
	"龙兽人": "dragon",
	"龙人": "dragon",
	"龙族": "dragon",
	"蜥蜴兽人": "Lizard",
	"蜥蜴人": "Lizard",
	"蜥蜴": "Lizard",
	"狗兽人": "dog",
	"狼兽人": "wolf",
	"狼人": "wolf",
	"狐狸兽人": "fox",
	"鱼兽人": "fish",
	"鱼人": "fish",
	"鲨鱼兽人": "shark",
	"鲨鱼": "shark",
	"海豚兽人": "dolphin",
	"海豚": "dolphin",
	"象兽人": "elephant",
	"袋鼠兽人": "kangaroo",
	"袋鼠": "kangaroo",
	"猴兽人": "monkey",
	"鼠兽人": "mouse",
	"豹兽人": "panther",
	"猪兽人": "pig",
	"兔兽人": "rabbit",
	"犀牛兽人": "rhinoceros",
	"犀牛人": "rhinoceros",
	"蛇兽人": "snake",
	"龟兽人": "turtle",
	"鲨狗兽人": "sergal",
	"鲨狗": "sergal",
	"鳄鱼": "Crocodile",
	"crocodile": "Crocodile",
	
	"赤熊": "bear",
	"橙熊": "bear",
	"黄熊": "bear",
	"青熊": "bear",
	"蓝熊": "bear",
	"紫熊": "bear",
	"黑熊": "bear",
	"白熊": "bear",
	"灰熊": "bear",
	"赤虎": "tiger",
	"橙虎": "tiger",
	"黄虎": "tiger",
	"青虎": "tiger",
	"蓝虎": "tiger",
	"紫虎": "tiger",
	"黑虎": "tiger",
	"白虎": "tiger",
	"灰虎": "tiger",
	"赤龙": "dragon",
	"橙龙": "dragon",
	"黄龙": "dragon",
	"青龙": "dragon",
	"蓝龙": "dragon",
	"紫龙": "dragon",
	"黑龙": "dragon",
	"白龙": "dragon",
	"灰龙": "dragon",
	"赤狼": "wolf",
	"橙狼": "wolf",
	"黄狼": "wolf",
	"青狼": "wolf",
	"蓝狼": "wolf",
	"紫狼": "wolf",
	"黑狼": "wolf",
	"白狼": "wolf",
	"灰狼": "wolf",
	"赤狗": "dog",
	"橙狗": "dog",
	"黄狗": "dog",
	"青狗": "dog",
	"蓝狗": "dog",
	"紫狗": "dog",
	"黑狗": "dog",
	"白狗": "dog",
	"灰狗": "dog",
	"赤豹": "panther",
	"橙豹": "panther",
	"黄豹": "panther",
	"青豹": "panther",
	"蓝豹": "panther",
	"紫豹": "panther",
	"黑豹": "panther",
	"白豹": "panther",
	"灰豹": "panther",
	"赤象": "elephant",
	"橙象": "elephant",
	"黄象": "elephant",
	"青象": "elephant",
	"蓝象": "elephant",
	"紫象": "elephant",
	"黑象": "elephant",
	"白象": "elephant",
	"灰象": "elephant",
	"赤马": "horse",
	"橙马": "horse",
	"黄马": "horse",
	"青马": "horse",
	"蓝马": "horse",
	"紫马": "horse",
	"黑马": "horse",
	"白马": "horse",
	"灰马": "horse",
	"赤羊": "sheep",
	"橙羊": "sheep",
	"黄羊": "sheep",
	"青羊": "sheep",
	"蓝羊": "sheep",
	"紫羊": "sheep",
	"黑羊": "sheep",
	"白羊": "sheep",
	"灰羊": "sheep",
	"赤鼠": "mouse",
	"橙鼠": "mouse",
	"黄鼠": "mouse",
	"青鼠": "mouse",
	"蓝鼠": "mouse",
	"紫鼠": "mouse",
	"黑鼠": "mouse",
	"白鼠": "mouse",
	"灰鼠": "mouse",
	"赤兔": "rabbit",
	"橙兔": "rabbit",
	"黄兔": "rabbit",
	"青兔": "rabbit",
	"蓝兔": "rabbit",
	"紫兔": "rabbit",
	"黑兔": "rabbit",
	"白兔": "rabbit",
	"灰兔": "rabbit",
	"赤猴": "monkey",
	"橙猴": "monkey",
	"黄猴": "monkey",
	"青猴": "monkey",
	"蓝猴": "monkey",
	"紫猴": "monkey",
	"黑猴": "monkey",
	"白猴": "monkey",
	"灰猴": "monkey",
	"赤牛": "bull",
	"橙牛": "bull",
	"黄牛": "bull",
	"青牛": "bull",
	"蓝牛": "bull",
	"紫牛": "bull",
	"黑牛": "bull",
	"白牛": "bull",
	"灰牛": "bull",
	"赤猫": "cat",
	"橙猫": "cat",
	"黄猫": "cat",
	"青猫": "cat",
	"蓝猫": "cat",
	"紫猫": "cat",
	"黑猫": "cat",
	"白猫": "cat",
	"灰猫": "cat",
	"赤猪": "pig",
	"橙猪": "pig",
	"黄猪": "pig",
	"青猪": "pig",
	"蓝猪": "pig",
	"紫猪": "pig",
	"黑猪": "pig",
	"白猪": "pig",
	"灰猪": "pig",
	"赤蛇": "snake",
	"橙蛇": "snake",
	"黄蛇": "snake",
	"青蛇": "snake",
	"蓝蛇": "snake",
	"紫蛇": "snake",
	"黑蛇": "snake",
	"白蛇": "snake",
	"灰蛇": "snake",
	"赤龟": "turtle",
	"橙龟": "turtle",
	"黄龟": "turtle",
	"青龟": "turtle",
	"蓝龟": "turtle",
	"紫龟": "turtle",
	"黑龟": "turtle",
	"白龟": "turtle",
	"灰龟": "turtle",
	
	"福瑞": "furry",
	"兽族": "furry",
	"兽人": "furry",
	"兽兽": "furry",
	"纯兽": "non-anthro",
	"人类": "Human",
	"鸟人": "Harpy",
	"机器人": "Robot",
	"史莱姆": "Slime",
	"触手": "Tentacles",
	"吸血鬼": "Vampire",
	"人皮服装": "SkinSuit",
	"怪物": "Monser",
	"英雄": "Hero",
	"警察": "Police",
	"特警": "Police",
	"魔王": "DevilKing",
	"恶魔": "Devil",
	"勇者": "Brave",
	"魅魔": "Succubus",
	"医生": "Doctor",
	
}