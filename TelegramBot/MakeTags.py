#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import shutil
import logging

from opencc import OpenCC

from FileOperate import openJson, saveJson, removeFile, timer
from TextFormat import isAlpha
from config import testMode

hashtags, entags, cntags, races, others, races_tw, others_tw = {}, {}, {}, {}, {}, {}, {}
racetags, racedict, racelist = {}, {}, []
json0 = os.path.join(os.getcwd(), "backup", "hashtags.json")  # 备用标签数据文件
json1 = os.path.join(os.getcwd(), "data", "hashtags.json")    # 主要标签数据文件
json2 = os.path.join(os.getcwd(), "data", "usedtags.json")    # 读取 entags,cntags
json3 = os.path.join(os.getcwd(), "data", "races.json")       # 读取 races,others
json4 = os.path.join(os.getcwd(), "data", "racedict.json")    # 讀取 racedict.json 會更慢


def makeHashTags(dic: dict) -> dict:  # DictNovel 原始tags生成 hashtags.json
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


def makeUsedTags() -> tuple[dict, dict]:  # tags.json 生成 usedtags.json
	dic = openJson(json1)
	usedtags = {}
	for keys, values in dic.items():
		for value in values.values():
			# print(f'"{value}": "{keys}"')
			if " " in keys:  # 1标签对应1个 list
				key = keys.split()   # 多标签处理
			else:
				key = [keys]
				
			usedtags[value] = key
			if isAlpha(value):  # 非中文转小写
				usedtags[value.lower()] = key
			if "中" not in value:  # 不转换语言标签“中文”
				usedtags[OpenCC('s2twp.json').convert(value)] = key
			
	for key, value in usedtags.items():
		if isAlpha(key):
			entags[key] = value
		else:
			cntags[key] = value
	return entags, cntags


def makeRaceTags():  # 翻譯標簽使用的標簽
	for key, val in races.items():
		# print(key, val)
		racetags[key] = [val.capitalize()]  # 数据结构 dict={str:list}
		racetags[val] = [val.capitalize()]  # 使用统一使用大写
		racetags[val.capitalize()] = [val.capitalize()]
		
	
def makeRaceDict():  # 搜索正文使用的關鍵詞
	hoof = "牛 马 羊 鹿 猪 象".split(" ")
	fish = "鱼 鲨 鳄 海豚 鲸 蛇".split(" ")
	prefix = "赤 红 橙 黄 绿 青 蓝 紫 黑 白 灰 棕 粉 小 胶".split(" ")
	suffix = "兽 人 族 头 吻 身 尾".split(" ")
	r18suffix = "棒 根 鞭 穴".split(" ")
	prefix2 = "紅 黃 綠 藍 灰 膠".split(" ")
	suffix2 = "獸 頭".split(" ")
	
	for i in races:
		# if len(i) == 1:  # 不處理雙字物種？
		for j in prefix:  # 添加前缀
			racedict[j + i] = [races[i].capitalize()]
		for j in suffix:  # 添加后缀
			racedict[i + j] = [races[i].capitalize()]
			
		if i in hoof:  # 脚，蹄，爪，处理
			racedict[i + "蹄"] = [races[i].capitalize()]
		elif i in fish:
			pass
		else:
			racedict[i + "爪"] = [races[i].capitalize()]
		
		for j in r18suffix:  # 添加后缀
			racedict[i + j] = [races[i].capitalize(), "R18"]
	for i in others:
		racedict[i] = [others[i].capitalize()]
		
	for i in races_tw:  # 繁體中文標簽
		for j in prefix2:  # 添加前缀
			racedict[j + i] = [races_tw[i].capitalize()]
		for j in suffix2:  # 添加后缀
			racedict[i + j] = [races_tw[i].capitalize()]
	for i in others_tw:
		racedict[i] = [others_tw[i].capitalize()]
	
	racedict.pop("龟头", None)  # 刪除奇怪的標簽
	racedict.pop("龜頭", None)
	# saveJson(json4, racedict)  # 讀josn會更慢
	

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
	
	
@timer
def updateUsedTagsJson():
	if os.path.exists(json1):  # 保证两者一致
		logging.info(f"Backing up {os.path.basename(json1)}")
		shutil.copy2(json1, json0)
	else:
		logging.info(f"Making Json1 From {os.path.basename(json0)}")
		shutil.copy2(json0, json1)
		
	if not os.path.exists(json2):
		logging.info(f"Making {os.path.basename(json2)}")
		saveJson(json2, makeUsedTags())


def updateRaceJson():
	def convert(dict0: dict):
		dict1 = {}
		dict2 = {"熊貓": "貓熊", "鯊狗": "鯊格魯", }
		for key1 in dict0:
			key2 = OpenCC('s2twp.json').convert(key1)
			value = dict0[key1]
			if key2 in dict2:  # 特殊種族名稱
				key2 = dict2[key2]
			if key2 != key1:
				dict1[key2] = value
		return dict1
	
	global races, others, races_tw, others_tw
	races, others, _, _ = openJson(json3)
	races_tw, others_tw = convert(races), convert(others)
	saveJson(json3, [races, others, races_tw, others_tw])


def updateJsons():
	removeFile(json2)
	updateUsedTagsJson()
	updateRaceJson()
	
	
def main():
	if not os.path.exists(json2):
		updateUsedTagsJson()
	global hashtags, entags, cntags, races, others, races_tw, others_tw
	entags, cntags = openJson(json2)
	hashtags = {**entags, **cntags}  # 合并dict
	races, others, races_tw, others_tw = openJson(json3)
	racelist.extend(list(races.values()))
	racelist.extend(list(others.values()))
	makeRaceTags()
	makeRaceDict()


@timer
def test():
	pass
	
	
if True:  # 初始化
	testMode = 0
	if testMode:
		updateJsons()
	main()
	# test()
	

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
	