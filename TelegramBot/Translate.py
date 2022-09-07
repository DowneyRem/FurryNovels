#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
from platform import platform
from locale import getdefaultlocale
from requests.exceptions import SSLError

from opencc import OpenCC
from pygtrans import Translate

from FileOperate import openText, saveText, findFile, timer, monthNow
from TextFormat import formatText
from config import proxy_list, default_path, cjklist, testMode
from translated import langs, words, wordsdict


local_times, google_times = 0, 0
# 设置翻译格式，设置代理
if "Windows" in platform():
	# client = Translate(fmt="text", proxies={'https': 'http://127.0.0.1:10808'})
	client = Translate(fmt="text", proxies={'https': proxy_list[0]})
elif "Linux" in platform():
	client = Translate(fmt="text")


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
	
	
def translateText(text: str, *, lang2: str, lang1="", mode=0) -> str:
	# lang1 原始语言，lang2 目标语言
	# mode==0 不处理，mode==1 添加空行与首行空格
	translated = []
	textlist = text.split("\n")
	
	try:
		if lang1:
			texts = client.translate(textlist, target=lang2, source=lang1)
		else:
			texts = client.translate(textlist, target=lang2)
			lang1 = texts[0].detectedSourceLanguage
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
		
		if mode == 0:
			text = "\n".join(translated)
		else:   # 优化翻译：前4行不添加空格，后面正常排版
			text = "\n".join(translated[5:])
			text = formatText(text, lang2)
			text = "\n".join(translated[:5]) + text
		# print(text)
		return text


def translate(text: str, *, lang2: str, lang1="", mode=0) -> str:
	# lang1 原语言， lang2 目标语言
	# mode==0 不处理，mode==1 添加空行与首行空格
	if not lang1:
		lang1 = getLang(text)
	if not lang2:
		lang2 = getLangSystem()
	
	if lang1 != lang2:
		if "zh" in lang1 and "zh" in lang2:
			text = convertText(text, lang1=lang1, lang2=lang2)
		else:
			text = translateText(text, lang1=lang1, lang2=lang2, mode=mode)
	return text
	
	
# 获取固定词的翻译
def getTranslatedWordsDict():
	# words = "author url hashtags others single translated".split(" ")
	words = "单篇小说 译文".split(" ")
	# words = ['Workspace', 'Computer', 'Monitor', 'Software', 'Scanner', 'Graphic tablet', 'Mouse', 'Printer','Things on your desk', 'Background music', 'Table', 'Chair', 'Others']
	# langs = "en".split(" ")
	
	wordsdict = {}
	print("", "wordsdict = {")
	for lang in langs:
		d1 = {}
		for word in words:
			try:
				d1[word] = translateText(word, lang2=lang)
			except AttributeError:
				d1[word] = ""
		wordsdict[lang] = d1
		print(f'"{lang}": {d1},')
	print("}")
	# print(f"{wordsdict}=")
	
	
# 本地方法翻译固定词组
def transWords(word: str, lang: str) -> str:
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


def translateFile(path: str, lang2=getLangSystem()) -> [str, None]:
	text = openText(path)
	lang1 = getLang(text)
	trans_dir = transDir(lang2)
	
	if lang1 != lang2 and (trans_dir not in path):
		dir2 = []   # 构造翻译文件路径
		dir1 = path.replace(f"{default_path}\\", "")
		dir1 = dir1.replace(f"{os.getcwd()}\\Novels\\", "")
		dir1 = dir1.split("\\")
		for text0 in client.translate(dir1, target=lang2):
			dir2.append(text0.translatedText)
		dir2 = "\\".join(dir2)
		trans_path = os.path.join(default_path, trans_dir, dir2)
		# print(dir1, dir2, sep="\n")
		# print(path)
		
		text = translate(text, lang1=lang1, lang2=lang2, mode=1)
		saveText(trans_path, text)
		return trans_path
	
	
# @timer
def main(lang2=getLangSystem()):
	trans_number = 0
	if default_path.endswith(monthNow()):   # 翻译 Novels 目录下所有小说
		path = default_path.replace(monthNow(), "")
	else:
		path = default_path
	print(f"当前目录：{path}")
	
	texts = findFile(path, ".txt")
	for path in texts:
		name = os.path.basename(path)
		path = translateFile(path, lang2)
		if path:
			trans_number += 1
			logging.info(path)
			print(f"已翻译第{trans_number}篇：{name}")
	print(f"已翻译【Novels】内{len(texts)}篇中的{trans_number}篇小说")
	
	
@timer
def test():
	print("测试")
	# getTranslatedWordsDict()
	
	
if __name__ == "__main__":
	# testMode = 0
	if testMode:
		test()
	else:
		main()
		
		