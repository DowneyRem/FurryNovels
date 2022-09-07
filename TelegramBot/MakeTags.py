#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

from opencc import OpenCC

from FileOperate import openJson, saveJson, newFilePathInCurrentDir, removeFile, timer
from config import testMode


hashtags, entags, cntags, racedict, racelist = {}, {}, {}, {}, []
json1 = newFilePathInCurrentDir("tags.json")
json2 = newFilePathInCurrentDir("tagsused.json")
json3 = newFilePathInCurrentDir("tagsen.json")
json4 = newFilePathInCurrentDir("tagscn.json")


def is_all_chinese(string: str) -> bool:  # 检验是否全是中文字符
	for char in string:
		if not "\u4e00" <= char <= "\u9fa5":
			return False
	return True


def is_contains_chinese(string: str) -> bool: # 检验是否含有中文字符
	for char in string:
		if "\u4e00" <= char <= "\u9fa5":
			return True
	return False


@timer
def makeTagsData(dic: dict) -> dict:  # DictNovel 原始tags生成 tags.json
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
	return d0


@timer
def makeTagsDict(dic: dict) -> dict:  # tags.json 生成 tagsused.json
	tagsused = {}
	for keys, values in dic.items():
		for value in values.values():
			# print(f'"{value}": "{keys}"')
			if " " in keys:  # 1标签对应1个 list
				key = keys.split()   # 多标签处理
			else:
				key = [keys]
				
			tagsused[value] = key
			# if value.isalpha():   # 中文也是True
			if not is_contains_chinese(value):
				tagsused[value.lower()] = key
				# tagsused[value.upper()] = key
				tagsused[value.capitalize()] = key
			if "中" not in value:  # 不转换语言标签“中文”
				tagsused[OpenCC('tw2sp.json').convert(value)] = key
				tagsused[OpenCC('s2twp.json').convert(value)] = key
	
	# if __name__ == "__main__" and testMode:  # 输出dict
	# 	for key, value in tagsused.items():
	# 		print(f"{key}: {value}")
	return tagsused


def makeRaceDict() -> tuple[dict, list]:
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
			racedict[j + i] = [races[i].capitalize()]
		for j in suffix:  # 添加后缀
			racedict[i + j] = [races[i].capitalize()]
		for j in r18suffix:  # 添加后缀
			racedict[i + j] = [races[i].capitalize(), "R18"]
	for i in others:
		racedict[i] = [others[i].capitalize()]
	
	racelist.extend(list(races.values()))
	racelist.extend(list(others.values()))
	return racedict, racelist


def cmp(a, b) -> int:  # 按dict内部顺序进行排序
	def getindex(obj: any):
		li = []
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
	dict0 = {}
	if not os.path.exists(json1):
		data = makeTagsData(dict0)
		saveJson(json1, data)
	
	
def makeJson2():
	if not os.path.exists(json2):
		makeJson1()
		data = makeTagsDict(openJson(json1))
		saveJson(json2, data)
	
	
def makeJson3():
	makeJson2()
	global hashtags
	hashtags = openJson(json2)
	for key, value in hashtags.items():
		# if __name__ == "__main__" and testMode:
		# 	print(f"{key}: {value}")
		
		# if key.isalpha():  # 中文也是True
		if is_all_chinese(key):
			cntags[key] = value
		else:
			entags[key] = value
	
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
	
	
if True:  # 初始化
	makeRaceDict()
	main()


if __name__ == "__main__":
	print(len(hashtags), len(entags), len(cntags))
	print(len(racedict), len(racelist))
	pass
	