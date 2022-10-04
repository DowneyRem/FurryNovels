#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import shutil
import logging

from opencc import OpenCC

from FileOperate import openJson, saveJson, removeFile, timer
from TextFormat import isAlpha
from config import testMode


hashtags, entags, cntags, racedict, racelist, racetags = {}, {}, {}, {}, [], {}
json0 = os.path.join(os.getcwd(), "backup", "tags.json")
json1 = os.path.join(os.getcwd(), "data", "tags.json")  # 主要数据文件
json2 = os.path.join(os.getcwd(), "data", "tagsused.json")
json3 = os.path.join(os.getcwd(), "data", "tagsen.json")
json4 = os.path.join(os.getcwd(), "data", "tagscn.json")
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


@timer
def makeTags(dic: dict) -> dict:  # DictNovel 原始tags生成 tags.json
	n = 0
	d0, d1 = {}, {}
	keys = list(dic.keys())
	for i in range(len(keys)):
		key, val = keys[i], dic[keys[i]]
		# print(f"{i}: {key=} {val=}")
		
		if i >= 1:
			last_key, last_val = keys[i - 1], dic[keys[i - 1]]
		else:
			last_key, last_val = "", ""
		
		if val != last_val and key != last_key:  # 重置序号与d1
			n = 0; d1 = {}
		if d1 == {}:  # 重置后填入第一组数据
			d1["en"] = val
			d1["zh"] = key
		
		# print(f"{last_key=} {last_val=}")
		while val == last_val and key != last_key:
			n += 1
			d1[f"zh{n}"] = key
			# print(f"zh{n}={key}")
			break
		d0[val] = d1
		
	if __name__ == "__main__" and testMode:  # 输出dict
		string = str(d0).replace("'", '"')
		print(string)
	saveJson(json1, d0)
	return d0


@timer
def makeTagsUsed() -> dict:  # tags.json 生成 tagsused.json
	dic = openJson(json1)
	tagsused = {}
	for keys, values in dic.items():
		for value in values.values():
			# print(f'"{value}": "{keys}"')
			if " " in keys:  # 1标签对应1个 list
				key = keys.split()   # 多标签处理
			else:
				key = [keys]
				
			tagsused[value] = key
			if isAlpha(value):  # 非中文转小写
				tagsused[value.lower()] = key
			if "中" not in value:  # 不转换语言标签“中文”
				tagsused[OpenCC('s2twp.json').convert(value)] = key
	
	# if __name__ == "__main__" and testMode:  # 输出dict
	# 	for key, value in tagsused.items():
	# 		print(f"{key}: {value}")
	return tagsused


def makeRaceTags():
	for key, val in races.items():
		# print(key, val)
		racetags[key] = [val]  # 数据结构 dict={str:list}
		racetags[val] = [val]
		
	
def makeRaceDict():
	prefix = "赤 红 橙 黄 绿 青 蓝 紫 黑 白 灰 棕 粉 小 胶".split(" ")
	suffix = "兽人 兽 人 族 头 吻 身 爪 脚 尾".split(" ")
	r18suffix = "棒 根 鞭 穴".split(" ")
	
	for i in races:
		for j in prefix:  # 添加前缀
			racedict[j + i] = [races[i].capitalize()]
		for j in suffix:  # 添加后缀
			racedict[i + j] = [races[i].capitalize()]
		for j in r18suffix:  # 添加后缀
			racedict[i + j] = [races[i].capitalize(), "R18"]
	for i in others:
		racedict[i] = [others[i].capitalize()]
	
	racedict.pop("龟头", None)
	racedict.pop("马眼", None)
	racelist.extend(list(races.values()))
	racelist.extend(list(others.values()))


def cmp(a, b) -> int:  # 按dict内部顺序进行排序
	def getindex(obj: any):
		li = []
		hashtags.update(racetags)
		li0 = list(hashtags.values())
		for item in li0:  # 从嵌套列表重获取排序
			if item not in li:
				li.extend(item)
		try:
			index = li.index(obj)
		except ValueError:
			index = len(li)
		return index
	
	a, b = getindex(a), getindex(b)
	if a > b:
		return 1
	elif a < b:
		return -1
	else:
		return 0
	
	
def makeJson1():
	if not os.path.exists(json1):
		logging.info(f"Making Json1")
		shutil.copy2(json0, json1)
	
	
@timer
def makeJson2():
	makeJson1()
	if not os.path.exists(json2):
		# logging.info(f"Backing up {os.path.basename(json1)}")
		# shutil.copy2(json1, json0)
		
		logging.info(f"Making {os.path.basename(json2)}")
		saveJson(json2, makeTagsUsed())
	
	
def makeJson3():
	makeJson2()
	logging.info(f"Making {os.path.basename(json3)}, {os.path.basename(json4)}")
	hashtags = openJson(json2)
	for key, value in hashtags.items():
		# if __name__ == "__main__" and testMode:
		# 	print(f"{key}: {value}")
		
		if isAlpha(key):
			entags[key] = value
		else:
			cntags[key] = value
	
	# print(entags, cntags ,sep="\n\n")
	saveJson(json3, entags)
	saveJson(json4, cntags)
	
	
def remakeJsons():
	removeFile(json2, json3, json4)
	makeJson3()
	
	
def main():
	if not os.path.exists(json3):
		makeJson3()
	global hashtags, entags, cntags
	hashtags = openJson(json2)
	entags = openJson(json3)
	cntags = openJson(json4)
	makeRaceDict()
	makeRaceTags()
	
	
if True:  # 初始化
	# testMode = 1
	if testMode:
		remakeJsons()
	main()
	

if __name__ == "__main__":
	print(len(hashtags), len(entags), len(cntags))
	print(len(racetags), len(racedict), len(racelist))
	# for key, val in hashtags.items():
	# 	print(f"{key}: {val}")
	# for key, val in racetags.items():
	# 	print(f"{key}: {val}")
	# for key, val in racedict.items():
	# 	print(f"{key}: {val}")
	# print(racelist)
	pass
	