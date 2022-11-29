#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
from platform import platform
from locale import getdefaultlocale
from requests.exceptions import SSLError

from opencc import OpenCC
from pygtrans import Translate

from FileOperate import readFile, saveFile, zipFile, unzipFile
from FileOperate import timer, removeFile, findFile
from TextFormat import formatText
from config import proxy_list, novel_path, translation_path, cjklist, monthNow, testMode


# 设置翻译格式，设置代理
if "Windows" in platform():
	# client = Translate(fmt="text", proxies={'https': 'http://127.0.0.1:10808'})
	client = Translate(fmt="text", proxies={'https': proxy_list[0]})
elif "Linux" in platform():
	client = Translate(fmt="text")

local_times, google_times = 0, 0
wordsdict, langs, words = {}, [], []
# langs = "en zh zh_cn zh_tw fr ru ar es de pt ja ko hi".split(" ")
json1 = os.path.join(os.getcwd(), "data", "translation.json")    # 主用数据文件
json2 = os.path.join(os.getcwd(), "data", "translated.json")     # 新翻译存放文件


# 判断语言
def getLangCharacter(text: str) -> str:  # 添加语言标签
	lang = ""
	list1 = "边 变 并 从 点 东 对 发 该 个 给 关 过 还 后 欢 会 机 几 间 见 将 进 经 觉 开 来 里 两 吗 么 没 们 难 让 时 实 说 虽 为 问 无 现 样 应 于 与 则 这 种".split(" ")
	list2 = "邊 變 並 從 點 東 對 發 該 個 給 關 過 還 後 歡 會 機 幾 間 見 將 進 經 覺 開 來 裡 兩 嗎 麼 沒 們 難 讓 時 實 說 雖 為 問 無 現 樣 應 於 與 則 這 種".split(" ")
	list3 = "あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の は ひ ふ へ ほ ま み む め も や ゆ よ ら り る れ ろ わ を ん が ぎ ぐ げ ご ざ じ ず ぜ ぞ だ ぢ づ で ど ぱ ぴ ぷ ぺ ぽ ば び ぶ べ ぼ ぁ ぃ ぅ ぇ ぉ っ ア イ ウ エ オ カ キ ク ケ コ サ シ ス セ ソ タ テ ツ テ ト ナ ニ ヌ ネ ノ ハ ヒ フ ヘ ホ マ ミ ム メ モ ヤ ユ ヨ ラ リ ル レ ロ ワ ヲ ン ガ ギ グ ゲ ゴ ザ ジ ズ ゼ ゾ ダ ヂ ヅ デ ド パ ピ プ ペ ポ バ ビ ブ ベ ボ ァ ィ ゥ ェ ォ ッ".split(" ")
	list4 = "하 수 사 우 아 대 그 나 문 생 모 만 경 어 자 다 여 정 보 가 함 지 시 누 세 운 퍼 학 바 무 국 얼 이 방 새 과 특 교 선 예 역 결 내 물 일 중 느 너 의 엄 남 작 상 더 최 환 컴 먼 부 기 거 오 광 민 람 리 니 러 제 각 르 들 떤 신 도 께 간 구 계 동 센 로 엇 굴 번 법 롭 히 육 술 용 론 요 끼 미 마 편 품 황 욱 근 퓨 저 분 업 늘 고 족".split(" ")

	cnt_map = {}
	# Process text in advance
	for i in text:
		if i not in cnt_map:
			cnt_map[i] = 1
		else:
			cnt_map[i] += 1

	def countChar(langlist: list):
		textnum = len(text)
		j = 0
		for char in langlist:  # Complexity: O(n * m)
			if char not in cnt_map:
				continue
			charnum = cnt_map[char]
			if 2000 * charnum / textnum >= 1:  # 测试过汉字
				j += 1
		logging.debug(f"{j}, {textnum}, {(1000*j)/textnum}")
		return j
	
	if countChar(list4) >= 0.1 * len(list4):  # 按 0.01 x 108 个谚文计算
		lang += "ko"
	elif countChar(list3) >= 0.1 * len(list3):  # 按 0.1 x 154 个假名计算
		lang += "ja"
	elif countChar(list2) >= 0.4 * len(list2):  # 按 0.4 x 50 个常用字计算
		lang += "zh_tw"
	elif countChar(list1) >= 0.4 * len(list1):  # 按 0.4 x 50 个常用字计算
		lang += "zh_cn"
	
	global local_times
	local_times += 1
	logging.debug(f"本地检测：{local_times}, {lang}")
	return lang
	
	
def getLangUnicode(text: str) -> str:
	langdict = {
		"ko": [0xac00, 0xd7a3],     # 谚文范围
		"ja": [0x3040, 0x30ff],     # 假名范围
		"zh_tw": [0x3100, 0x312f],  # 注音范围
		}
	
	lang = ""
	for key in langdict:
		charnum = 0
		for char in text:
			if langdict[key][0] <= ord(char) <= langdict[key][1]:
				charnum += 1
		if 2000 * charnum / len(text) >= 1:  # 测试过汉字
			lang += key
	return lang
	
	
def getLangOffline(text: str) -> str:
	lang = set()
	if text:
		lang.add(getLangCharacter(text))
		lang.add(getLangUnicode(text))
		lang = "".join(lang)
	return lang
	
	
def getLangGoogle(text: str) -> str:
	try:
		lang = client.detect(text).language
		lang = lang.lower().replace("-", "_")  # 格式化成 zh_cn
	except SSLError as e:
		logging.error(f"网络错误：\n{e}")
	except Exception as e:
		logging.error(e)
	else:
		global google_times
		google_times += 1
		logging.info(f"谷歌检测：{google_times}, {lang}")
		return lang
	
	
def getLang(text: str) -> str:
	if len(text) >= 5000:
		text = text[:5000]
	lang = getLangCharacter(text)
	# lang = getLangOffline(text)
	if not lang:
		lang = getLangGoogle(text)
	return lang
	
	
def getLanguage(text: str) -> str:
	return getLang(text)
	
	
def getLangSystem() -> str:
	return getdefaultlocale()[0].lower()


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
		lang1 = getLang(text)
	if not lang2:
		lang2 = getLangSystem()
	if "zh-hans" in lang2:
		lang2 = "zh_cn"
	elif "zh-hant" in lang2:
		lang2 = "zh_tw"
	
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
	lang1 = getLang(text)
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
		