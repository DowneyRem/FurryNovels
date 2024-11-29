#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import sys
import time
import logging
from platform import platform
from functools import wraps
from requests.exceptions import SSLError

from opencc import OpenCC
from pygtrans import Translate

try:
	from func_timeout import func_set_timeout, FunctionTimedOut
except (ImportError) as e:
	logging.info(f"{e}")
	
from FileOperate import readFile, saveFile, zipFile, unzipFile
from FileOperate import timer, removeFile, findFile, openFile
from GetLanguage import getLanguage, getLangSystem
from TextFormat import formatText
from configuration import novel_folder, trans_folder, proxy_list, cjklist, testMode


# 设置翻译格式，设置代理
client = Translate(fmt="text", proxies={'https': proxy_list[0]})
local_times, google_times = 0, 0

# 固定词组本地翻译
wordsdict, langs, words = {}, [], []
# langs = "en zh zh_cn zh_tw fr ru ar es de pt ja ko hi".split(" ")
json1 = os.path.join(os.path.dirname(__file__), "data", "translation.json")    # 主用数据文件
json2 = os.path.join(os.path.dirname(__file__), "data", "translated.json")     # 新翻译存放文件

# 翻译时所用文件夹
down_folder = os.path.join(trans_folder, "Download")
zip_folder = os.path.join(trans_folder, "ZipFiles")
File_path = ""  # 拼接文件路径


def onWindows(function):
	@wraps(function)
	def wrapper(*args, **kwargs):
		result = ""
		if "Windows" in platform():  # 导入 win32 特有库
			try:
				global msvcrt
				import msvcrt
			except (ModuleNotFoundError, ImportError) as e:
				# print("不存在: msvcrt")
				logging.error(e)
			else:
				result = function(*args, **kwargs)
		else:
			logging.error(f"非 Windows 不可执行 {function.__name__}")
		return result
	return wrapper


# 翻译/文字转换
class TranslateWords:
	pass


def convertText(text: str, *, lang2: str, lang1="") -> str:  # 原来是 language Telegram 语言包
	# lang1 原语言， lang2 目标语言
	if "zh_tw" in lang1 and ("zh-hans" in lang2 or "zh_cn" in lang2):
		text = OpenCC('tw2sp.json').convert(text)   # 繁体文件，转简体
		text = text.replace("「", "“").replace("」", "”").replace("『", "‘").replace("』", "’")
		
	elif "zh_cn" in lang1 and ("zh-hant" in lang2 or "zh_tw" in lang2):
		text = OpenCC('s2twp.json').convert(text)   # 简体文件，转繁体
		text = text.replace("“", "「").replace("”", "」").replace("‘", "『").replace("’", "』")
	return text
	
	
# @timer
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
		elif transWords("author", lang1) in text \
			or "by" in text or "By" in text:  # 前2行不添加空格
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
		
	lang1 = lang1.lower().replace("-", "_")
	lang2 = lang2.lower().replace("-", "_")
	if lang1 != lang2:
		if "zh" in lang1 and "zh" in lang2:
			text = convertText(text, lang1=lang1, lang2=lang2)
		else:
			text = translateText(text, lang1=lang1, lang2=lang2)
	return text
	
	
# 获取固定词的翻译
class TranslateFixedWords:
	pass


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
class TranslateFile:
	pass


def transDir(lang2="en") -> str:
	if "Linux" in platform():  # Linux 上统一使用英文目录
		trans_dir = transWords("translated", "en")
	else:
		trans_dir = transWords("translated", lang2)
	return trans_dir


def transPath(path, mode, *, lang1, lang2) -> str:
	trans_path = ""
	extname = os.path.splitext(path)[1].lower()  # 去后缀名再翻译
	if mode == 0:  # Pixiv 小说，构造翻译路径
		part_path = os.path.splitext(os.path.relpath(path, novel_folder))[0]
		if transDir(lang1) in part_path:
			part_path = os.path.relpath(part_path, transDir(lang1))
		part_path = translate(part_path, lang1=lang1, lang2=lang2).strip()
		trans_path = os.path.join(novel_folder, transDir(lang2), f"{part_path}{extname}")
		# FurryNovelsBot/Novels/2023/01/翻译/文件名.txt
		
	elif mode == 1:  # Trlegram 下载文件单独文件，构造翻译路径
		name = os.path.splitext(os.path.basename(path).strip().replace("_", " "))[0]
		name = translate(name, lang1=lang1, lang2=lang2).strip()
		trans_path = os.path.join(trans_folder, f"{name}{extname}")
		# FurryNovelsBot/Translation/2023/01/翻译/文件名.txt
	
	elif mode == 2:  # Trlegram 下载zip文件，构造翻译路径
		# down_folder = os.path.join(trans_folder, "Download")
		# zip_folder = os.path.join(trans_folder, "ZipFiles")
		# FurryNovelsBot/Translation/Download
		# FurryNovelsBot/Translation/ZipFiles
		part_path = os.path.splitext(os.path.relpath(path, down_folder))[0]
		part_path = translate(part_path, lang1=lang1, lang2=lang2).strip()
		trans_path = os.path.join(zip_folder, f"{part_path}{extname}")
		# FurryNovelsBot/Translation/ZipFiles/文件名.txt
	
	# print(f"{path=}")
	# print(f"{trans_path=}")
	return trans_path
	
	
def translateDocument(text, lang1, lang2, path, mode=1):
	text = translate(text, lang1=lang1, lang2=lang2)
	trans_path = transPath(path, mode=mode, lang1=lang1, lang2=lang2)
	trans_path = saveFile(trans_path, text, template=path)
	# trans_path = saveDocx(trans_path, text, template=path)
	return trans_path


def transDocument(path: str, lang2=getLangSystem(), mode=1) -> str:
	text = readFile(path)
	lang1 = getLanguage(text)
	if lang1 == lang2:
		raise RuntimeError("语言一致，无需翻译")
	if lang1 != lang2 and lang1:
		if mode:  # 下载小说翻译mode==0；Tg翻译&拖入文件mode==1；zip内文件mode==2
			return translateDocument(text, lang1, lang2, path, mode)
		elif transDir(lang2) not in path:  # 过滤已翻译内容
			return translateDocument(text, lang1, lang2, path, mode)
	
	
def transZip(zippath, lang2=getLangSystem()) -> str:
	trans_files = []
	folder = unzipFile(zippath, path=down_folder)  # 指定解压目录
	# folder = unzipFile(zippath, delete=0)  # 指定解压目录
	files = findFile(folder, ".txt", ".docx")
	# if "Windows" in platform():  # 打开很慢
	# 	files.extend(findFile(folder, ".doc"))
	
	for file in files:
		try:
			trans_path = transDocument(file, lang2=lang2, mode=2)
		except RuntimeError:  # 语言一致，另存一份
			text = readFile(file)
			trans_path = transPath(file, lang1=lang2, lang2=lang2, mode=2)
			trans_path = saveFile(trans_path, text, template=file)
		trans_files.append(trans_path)
	
	# if len(trans_files) >= 2:
	# 	translated_folder = os.path.commonpath(trans_files)    # 可能压缩过多文件
	# else:
	# 	translated_folder = os.path.dirname(trans_files[0])
	zippath2 = os.path.join(trans_folder, f"{os.path.basename(folder)}.zip")
	zippath2 = zipFile(trans_files, zippath=zippath2, delete=1)  # 压缩所有文件
	removeFile([down_folder, zip_folder])  # 删除解压后的文件，压缩后的空文件夹
	return zippath2


@timer
def transFile(path: str, lang2=getLangSystem()) -> str:
	extnames = ".txt .docx .pdf".split()
	extname = os.path.splitext(path)[1].lower()
	# lang2 = "zh_tw"
	if path.lower().endswith(".zip"):
		return transZip(path, lang2=lang2)
	elif extname in extnames:
		return transDocument(path, lang2=lang2)
	else:
		raise AttributeError
	
	
# @timer
def transFiles(lang2=getLangSystem()):
	trans_number = 0
	path = os.path.join(os.getcwd(), "Novels")  # 翻译 Novels 目录下所有小说
	print(f"当前目录：{path}")
	files = findFile(path, ".txt", "docx")
	for file in files:
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
	print(f"已翻译【{name}】内{len(files)}篇中的{trans_number}篇小说")
	
	
class RunTranslate:
	pass


# @func_set_timeout(3)
def translateForRun(path: str):
	print(f"\n正在翻译：{path}")
	try:
		trans_path = transFile(path)
		# trans_path = transDocument(droppedFile)
	except (RuntimeError, AttributeError) as e:  # 语言一致跳过
		print(f"{e}")
	else:
		print(f"翻译完成：{trans_path}")
		return trans_path
	
	
def runInputToCMD():
	print("当前模式【CMD窗口】【不支持】【批量翻译】多个文件")
	droppedFile = input("\n请将要翻译的小说文件拖入至此页面，按 Enter 开始翻译：\n").strip()
	# droppedFile = droppedFile.replace("'", "").replace('"', '').replace('"', '').replace('“', '')
	droppedFile = re.sub('''['"“”]''', "", droppedFile)
	while droppedFile:
		if droppedFile:
			translateForRun(droppedFile)
		else:
			print("输入有误，请重新输入，退出请直接按 Enter 键")
		droppedFile = input("\n请将要翻译的小说文件拖入至此页面，按 Enter 开始翻译：\n").strip()
		
		
def runDrawToIcon():
	print("请将要翻译的小说文件【拖入翻译程序图标】使用")
	print("仅支持 txt docx zip 格式\n")
	
	if len(sys.argv) >= 2: # 拖入图标的文件
		for droppedFile in sys.argv[1:]:
			translateForRun(droppedFile)

try:
	@onWindows
	@func_set_timeout(0.1)
	def getInputFile(pre_str=""):
		global File_path
		File_path = pre_str  # 每次重新运行，清空
		while True:
			File_path += msvcrt.getwch()
except NameError as e:
	print(f"{e}\n")
	pass
	

@onWindows
def runDrawToCMD():
	"""
	python命令行窗口获取拖放文件路径
	https://www.jianshu.com/p/be2dcf7189e8
	"""
	global File_path
	print("请将要翻译的小说文件，拖入至此页面，即可开始翻译")
	print("仅支持【同一磁盘下】的 txt docx zip 文件")
	print("退出翻译请直接按 Enter 键\n")
	
	zero_chr = ""  # 二次运行时，无法获取路径首字母/盘符
	while True:
		time.sleep(0.5)
		first_chr = f"{msvcrt.getwch()}"
		if "\r" in first_chr:  # 退出翻译
			break
			
		while first_chr:
			try:
				getInputFile(f"{zero_chr}{first_chr}")
			except FunctionTimedOut:  # 不支持含有——的文件
				if not zero_chr:  # 获取首个文件的盘符
					zero_chr = first_chr
				if " " in File_path:  # 有空格时，会获取两次盘符
					File_path = File_path[1:].replace('"', '')
				if File_path.startswith(':'):
					File_path = f"{zero_chr}{File_path}"
					
				# print(f"{os.path.isfile(File_path)} {File_path}")
				translateForRun(File_path)
				break


def main():
	try:
		if len(sys.argv) >= 2:
			runDrawToIcon()  # 文件拖入图标
		elif len(sys.path) <= 10:
			runDrawToCMD()    # 文件拖入CMD
		else:  # Pycharm 内启动为11参数
			runInputToCMD()    # 输入文件路径
	except NameError:
		print("不安装 fun_timeout 无法使用【拖入CMD窗口】翻译")
		print("请将要翻译的小说文件【拖入翻译程序图标】使用\n")
	except Exception as e:
		print(f"{e}")
	else:
		openFile(trans_folder)
	finally:
		print("\n已退出翻译")
		time.sleep(5)
	

class Others:
	pass


def test2():
	lang2 = getLangSystem()
	# lang2 = "zh_tw"
	transFiles(lang2)


@timer
def test():
	print("测试")
	# makeTranslationJson()
	# updateWordsDict()
	
	
if __name__ == "__main__":
	testMode = 0
	if testMode:
		test()
	else:
		main()
		