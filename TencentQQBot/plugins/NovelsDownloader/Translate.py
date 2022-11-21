#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
from platform import platform
from requests.exceptions import SSLError

from opencc import OpenCC
from pygtrans import Translate

from .FileOperate import readFile, saveFile, zipFile, unzipFile
from .FileOperate import timer, removeFile, findFile
from .GetLanguage import getLanguage, getLangSystem
from .TextFormat import formatText
from .configuration import proxy_list, novel_path, translation_path, cjklist, monthNow, testMode


# 设置翻译格式，设置代理
if "Windows" in platform():
	# client = Translate(fmt="text", proxies={'https': 'http://127.0.0.1:10808'})
	client = Translate(fmt="text", proxies={'https': proxy_list[0]})
elif "Linux" in platform():
	client = Translate(fmt="text")


local_times, google_times = 0, 0
wordsdict, langs, words = {}, [], []
# langs = "en zh zh_cn zh_tw fr ru ar es de pt ja ko hi".split(" ")
json1 = os.path.join(os.path.dirname(__file__), "data", "translation.json")    # 主用数据文件
json2 = os.path.join(os.path.dirname(__file__), "data", "translated.json")     # 新翻译存放文件


# 翻译/文字转换
def convertText(text: str, *, lang2: str, lang1="") -> str:  # 原来是 language Telegram 语言包
	# lang1 原语言， lang2 目标语言
	if "zh_tw" in lang1 and ("zh-hans" in lang2 or "zh_cn" in lang2):
		text = OpenCC('tw2sp.json').convert(text)   # 繁体文件，转简体
		text = text.replace("「", "“").replace("」", "”").replace("『", "‘").replace("』", "’")
		
	elif "zh_cn" in lang1 and ("zh-hant" in lang2 or "zh_tw" in lang2):
		text = OpenCC('s2twp.json').convert(text)   # 简体文件，转繁体
		text = text.replace("“", "「").replace("”", "」").replace("‘", "『").replace("’", "』")
	return text
	
	
@timer
def translateText(text: (str, list), *, lang2: str, lang1="", mode=0) -> [str, tuple]:
	# lang1 原始语言，lang2 目标语言
	translated = []
	if isinstance(text, str):
		textlist = text.split("\n")
	else:
		textlist = text
		
	try:
		if lang1:
			texts = client.translate(textlist, target=lang2, source=lang1)
		else:
			texts = client.translate(textlist, target=lang2)
			lang1 = texts[0].detectedSourceLanguage.lower().replace("-", "_")
		# print(lang1, texts)
	
	except SSLError as e:
		logging.error(f"网络错误：\n{e}")
	except Exception as e:
		logging.error(e)
		
	else:
		for line in texts:
			translated.append(line.translatedText)
		
		global google_times
		google_times += 1
		logging.info(f"谷歌翻译：大段文本, {google_times}")
		
		if transWords("author", lang1) in text  \
			and transWords("url", lang1) in text \
			and transWords("hashtags", lang1) in text:  # 前4行不添加空格
			text = "\n".join(translated[5:])
			text = formatText(text, lang2)
			text = "\n".join(translated[:5]) + text
		elif transWords("author", lang1) in text or "by" in text or "By" in text:  # 前2行不添加空格
			text = "\n".join(translated[2:])
			text = formatText(text, lang2)
			text = "\n".join(translated[:2]) + text
		else:
			text = "\n".join(translated)
			
		if mode:
			return text, lang1
		else:
			return text


def translate(text: str, *, lang2: str, lang1="") -> str:
	# lang1 原语言， lang2 目标语言
	if not lang1:
		lang1 = getLanguage(text)
	if not lang2:
		lang2 = getLangSystem()
	if "zh-hans" in lang2:
		lang2 = "zh_cn"
	elif "zh-hant" in lang2:
		lang2 = "zh_tw"
		
	lang1 = lang1.lower().replace("-","_")
	lang2 = lang2.lower().replace("-","_")
	if lang1 != lang2:
		if "zh" in lang1 and "zh" in lang2:
			text = convertText(text, lang1=lang1, lang2=lang2)
		else:
			text = translateText(text, lang1=lang1, lang2=lang2)
	return text
	
	
# 获取固定词的翻译
def makeTranslationJson():
	words = "单篇小说 译文".split(" ")
	langs = "en zh zh_cn zh_tw fr ru ar es de pt ja ko hi".split(" ")
	wordsdict = {}
	for lang in langs:
		d1 = {}
		for word in words:
			try:
				d1[word] = translateText(word, lang2=lang)
			except AttributeError:
				d1[word] = ""
		wordsdict[lang] = d1
	
	dictlist = []
	dicts = readFile(json2)
	for dic in dicts:
		dictlist.append(dic)
	dictlist.append(wordsdict)
	saveFile(json2, dictlist)
	# updateWordsDict()


# 整合多个存放翻译的dict
@timer
def makeWordsDict():
	wordsdict = {}
	dicts = readFile(json2)
	langs = "en zh zh_cn zh_tw fr ru ar es de pt ja ko hi".split(" ")
	for lang1 in langs:
		d0 = {}
		for d1 in dicts:
			# print(d1)
			for lang2, d2 in d1.items():
				if lang1 == lang2:
					# print(lang1, d2)
					d0.update(d2)
					for key in d2:
						if key not in words:
							words.append(key)
		wordsdict[lang1] = d0
		
	logging.info(f"Making {os.path.dirname(json1)}")
	saveFile(json1, wordsdict)
	return wordsdict


def updateWordsDict():
	removeFile(json1)
	makeWordsDict()
	# readWordsDict()


# 本地方法翻译固定词组
def transWords(word: str, lang: str) -> str:
	if os.path.exists(json1):
		wordsdict = readFile(json1)
	else:
		wordsdict = makeWordsDict()
	langs = list(wordsdict.keys())
	words = list(wordsdict[langs[0]].keys())
	lang = lang.lower().replace("-", "_")
	if word in words and lang in langs:  # 确认所用词汇一定存在翻译
		translated_word = wordsdict.get(lang).get(word)
		
		global local_times
		local_times += 1
		logging.debug(f"本地翻译：{local_times}, {lang}")
	else:
		translated_word = translateText(word, lang2=lang)
		
	if word not in "single translated".split(" "):
		if lang in cjklist:
			translated_word = f"{translated_word}："  # 全角冒号
		else:
			translated_word = f"{translated_word}: "  # 冒号空格
		# print(translated_word)
	return translated_word

	
# 文件翻译部分
def transDir(lang2="en") -> str:
	if "Linux" in platform():  # Linux 上统一使用英文目录
		trans_dir = transWords("translated", "en")
	else:
		trans_dir = transWords("translated", lang2)
	return trans_dir


def transPath(path, mode, *, lang1, lang2):
	if mode == 0:  # Pixiv 小说，构造翻译路径
		part_path = os.path.relpath(path, novel_path)
		if transDir(lang1) in part_path:
			part_path = os.path.relpath(part_path, transDir(lang1))
		part_path = translate(part_path, lang1=lang1, lang2=lang2)
		trans_path = os.path.join(novel_path, transDir(lang2), part_path)
		
	elif mode == 1:  # Trlegram 下载文件单独文件，构造翻译路径
		name = os.path.basename(path)
		name = translate(name, lang1=lang1, lang2=lang2)
		trans_path = os.path.join(translation_path, monthNow(), name)
		
	else:  # Trlegram 下载zip文件，构造翻译路径
		down_folder = os.path.join(translation_path, "Download")
		zip_folder = os.path.join(translation_path, "ZipFiles")
		part_path = os.path.relpath(path, down_folder)
		part_path = translate(part_path, lang1=lang1, lang2=lang2)
		trans_path = os.path.join(zip_folder, part_path)
	# print(f"{path=}")
	# print(f"{trans_path=}")
	return trans_path


def transDocument(path: str, lang2=getLangSystem(), mode=1) -> str:
	text = readFile(path)
	lang1 = getLanguage(text)
	if lang1 == lang2:
		raise RuntimeError("语言一致，无需翻译")
	
	if lang1 != lang2 and lang1 and transDir(lang2) not in path:
		text = translate(text, lang1=lang1, lang2=lang2)
		trans_path = transPath(path, mode=mode, lang1=lang1, lang2=lang2)
		# saveDocx(trans_path, text, template=path)
		saveFile(trans_path, text, template=path)
		return trans_path
	
	
def transZip(zippath, lang2=getLangSystem()) -> str:
	trans_files = []
	folder = unzipFile(zippath, delete=0)
	files = findFile(folder, ".txt", ".docx")
	# if "Windows" in platform():  # 打开很慢
	# 	files.extend(findFile(folder, ".doc"))
	
	for file in files:
		try:
			trans_path = transDocument(file, lang2=lang2, mode=2)
		except RuntimeError:  # 语言一致
			text = readFile(file)
			trans_path = transPath(file, mode=2, lang1=lang2, lang2=lang2)
			saveFile(trans_path, text, template=file)
		trans_files.append(trans_path)
	
	removeFile(folder)  # 删除未翻译的文件
	if len(trans_files) >= 2:
		trans_fold = os.path.commonpath(trans_files)
	else:
		trans_fold = os.path.dirname(trans_files[0])
	zippath2 = zipFile(trans_fold, delete=1)
	# print(f"翻译完成：{zippath2}")
	return zippath2


@timer
def transFile(path: str, lang2=getLangSystem()) -> str:
	extnames = ".txt .docx".split()
	extname = os.path.splitext(path)[1].lower()
	if path.lower().endswith(".zip"):
		return transZip(path, lang2=lang2)
	elif extname in extnames:
		return transDocument(path, lang2=lang2)
	else:
		raise AttributeError
	
	
# @timer
def transFiles(path, lang2=getLangSystem()):
	trans_number = 0
	print(f"当前目录：{path}")
	texts = findFile(path, ".txt", "docx")
	for file in texts:
		try:
			if "Novels" in path:
				transDocument(file, lang2, mode=0)
			elif "Translation" in path:
				transDocument(file, lang2, mode=1)
		except RuntimeError:  # 语言一致跳过
			pass
		else:
			trans_number += 1
			print(f"已翻译{trans_number}篇：{os.path.basename(file)}")
			
	name = os.path.basename(path)
	print(f"已翻译【{name}】内{len(texts)}篇中的{trans_number}篇小说")
	
	
def main():
	path = os.path.join(os.getcwd(), "Novels")  # 翻译 Novels 目录下所有小说
	# path = os.path.join(translation_path, "Download")
	lang2 = getLangSystem()
	# lang2 = "zh_tw"
	transFiles(path, lang2)
	
	
@timer
def test():
	print("测试")
	# translateCommonWords()
	# updateWordsDict()
	
	
if __name__ == "__main__":
	testMode = 0
	if testMode:
		test()
	else:
		main()
		