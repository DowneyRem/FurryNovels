#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
from platform import platform

from pygtrans import Translate

from FileOperate import openTextLines, saveText, formatFileName
from config import proxy_windows


if "Windows" in platform():
	# client = Translate(fmt="text", proxies={'https': 'http://127.0.0.1:10808'})
	client = Translate(fmt="text", proxies={'https': proxy_windows[0]})
elif "Linux" in platform():
	client = Translate(fmt="text")


def getLang(text):  # 添加语言标签
	tags = ""
	list1 = "边 变 并 从 点 东 对 发 该 个 给 关 过 还 后 欢 会 机 几 间 见 将 进 经 觉 开 来 里 两 吗 么 没 们 难 让 时 实 说 虽 为 问 无 现 样 应 于 与 则 这 种".split(" ")
	list2 = "邊 變 並 從 點 東 對 發 該 個 給 關 過 還 後 歡 會 機 幾 間 見 將 進 經 覺 開 來 裡 兩 嗎 麼 沒 們 難 讓 時 實 說 雖 為 問 無 現 樣 應 於 與 則 這 種".split(" ")
	list3 = "あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の は ひ ふ へ ほ ま み む め も や ゆ よ ら り る れ ろ わ を ん が ぎ ぐ げ ご ざ じ ず ぜ ぞ だ ぢ づ で ど ぱ ぴ ぷ ぺ ぽ ば び ぶ べ ぼ ぁ ぃ ぅ ぇ ぉ ア イ ウ エ オ カ キ ク ケ コ サ シ ス セ ソ タ テ ツ テ ト ナ ニ ヌ ネ ノ ハ ヒ フ ヘ ホ マ ミ ム メ モ ヤ ユ ヨ ラ リ ル レ ロ ワ ヲ ン ガ ギ グ ゲ ゴ ザ ジ ズ ゼ ゾ ダ ヂ ヅ デ ド パ ピ プ ペ ポ バ ビ ブ ベ ボ ァ ィ ゥ ェ ォ".split(" ")
	list4 = "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c d e f g h I j k l m n o p q r s t u v w x y z".split(" ")
	
	def countChar(list):
		textnum = len(text)
		j = 0
		for i in range(len(list)):
			char = list[i]
			num = text.count(char)
			if 20000 * num / textnum >= 10:  # 测试过
				j += 1
		# print(j)
		return j
	
	if countChar(list3) >= 0.1 * len(list3):  # 按 0.1 x 152 个假名计算
		tags += "ja"
	if countChar(list2) >= 0.4 * len(list2):  # 按 0.4 x 50 个常用字计算
		tags += "zh_tw"
	if countChar(list1) >= 0.4 * len(list1):  # 按 0.4 x 50 个常用字计算
		tags += "zh_cn"
	if countChar(list4) >= 0.3 * len(list4):  # 按 0.3 x 52 个字母计算
		tags += "en"
	# print(tags)
	return tags

num = 0
def getLanguage(text):  # 添加语言标签
	language = client.detect(text).language
	if "zh" in language or "en" in language:
		language = getLang(text)
	# if not language:  # 谷歌也不知道是什么语言
	# 	language = "en"
	global num
	num += 1
	print("谷歌翻译：", num, language)
	return language


def translateText(text: str, lang: str) -> str:
	text = client.translate(text, lang)
	# print(text.translatedText)
	return text.translatedText


def translateTextList(textlist: list, lang) -> list:
	if type(textlist) == str:
		textlist = [textlist]
	texts = client.translate(textlist, lang)
	li = []
	for text in texts:
		li.append(text.translatedText)
	return li


def transWords(word: str, lang: str) -> str:
	l = "zh zh_cn zh_tw ja ko".split(" ")
	wordsdict = {
		'en': {'author': 'author', 'url': 'URL', 'hashtags': 'hashtags', 'others': 'others'},
		'zh': {'author': '作者', 'url': '网址', 'hashtags': '标签', 'others': '其他'},
		'zh_cn': {'author': '作者', 'url': '网址', 'hashtags': '标签', 'others': '其他'},
		'zh_tw': {'author': '作者', 'url': '網址', 'hashtags': '標籤', 'others': '其他'},
		'ja': {'author': '著者', 'url': 'URL', 'hashtags': 'ハッシュタグ', 'others': 'その他'},
		'ko': {'author': '작가', 'url': 'URL', 'hashtags': '해시태그', 'others': '기타'},
		'fr': {'author': 'auteur', 'url': 'URL', 'hashtags': 'hashtags', 'others': 'les autres'},
		'de': {'author': 'Autor', 'url': 'URL', 'hashtags': 'Hashtags', 'others': 'Andere'},
		'ru': {'author': 'автор', 'url': 'URL', 'hashtags': 'хэштеги', 'others': 'другие'},
		'es': {'author': 'autor', 'url': 'URL', 'hashtags': 'etiquetas', 'others': 'otros'},
		'pt': {'author': 'autor', 'url': 'URL', 'hashtags': 'hashtags', 'others': 'outros'},
		'hi': {'author': 'लेखक', 'url': 'यूआरएल', 'hashtags': 'हैशटैग', 'others': 'अन्य'},
		}
	
	try:
		words = wordsdict.get(lang)
		tword = words.get(word, None)
	except AttributeError:
		tword = translateText(word, lang)
	
	# 多语言处理， readline 再spilt(":")spilt("：")
	if lang in l:
		tword = f"{tword}："
	else:
		tword = f"{tword}: "
	# print(tword)
	return tword


def formatTextIndent(text):
	text = re.sub("\.{3,}", "……", text)  # 省略号标准化
	text = re.sub("。。。{3,}", "……", text)
	text = re.sub("!{3,}", "!{3}", text)  # 感叹号标准化
	text = re.sub("！{3,}", "！{3}", text)
	
	text = text.replace("\n", "\n　　")  # 首行2个全角空格
	text = re.sub("\n　{3,}", "\n", text)
	text = re.sub("\n{3,}", "\n\n", text)
	return text


def formatText(textlist, lang):
	info  = "" ; nomal = ""
	langdict = {
		"en" : "English",
		"zh" : "Chinese",
		"zh-CN" : "Simplified Chinese",
		"zh-TW" : "Traditional Chinese",
		"fr" : "French",
		"ru" : "Russian",
		"ar" : "Arabic",
		"es" : "Spanish",
		"de" : "German",
		"pt": "Portuguese",
		"ja": "Japanese",
		"kr": "Korean",
		"hi" : "Hindi",
		"" : "",
		}
	
	for i in range(0, 5):
		if i == 0:
			info += textlist[i] + "\n"
		else:
			t = textlist[i].split("：")   # 翻译：标签，其他
			if len(t) == 1:
				info += textlist[i] + "\n"
			else:
				info += translateTextList(t[0] + "： ", lang)[0] + t[-1] + "\n"
	
	for i in range(5, len(textlist)):
		nomal += textlist[i] + "\n"
		
	text = info + formatTextIndent(nomal)
	text = text.replace(" ", "")
	text = text.replace("​", "")
	text = text.replace("&quot;", "")
	text = text.replace("&#39;", "")
	return text


def translateFile(path, lang):
	#path 源文件，lang 翻译成什么语言
	name1 = os.path.basename(path).replace(".txt", "")
	textlist = openTextLines(path)
	lang1 = getLanguage(str(textlist))     # 原语言
	
	name2 = translateTextList(name1, lang)[0]  # 翻译
	name2 = formatFileName(name2).strip()
	textlist = translateTextList(textlist, lang)
	text = formatText(textlist, lang)
	# print(text, lang1, lang, sep="\n")

	path = os.path.join(os.getcwd(), "Novels", "翻译", f"{name2}.txt")
	saveText(path, text)
	print(f"【{name1}】已翻译", path, sep="\n")
	return path, lang1




if __name__=="__main__":
	# path = r"D:\Download\Github\FurryNovelsBot\Novels\《大学教授阿诺雷德》.txt"
	# translateFile(path, lang="en")
	# pass
	# a=translateText("你好","en")
	# print(a)
	
	def getWordsDict():
		a = "author url hashtags others".split(" ")
		langs = "en zh_cn zh_tw fr ru ar es de pt ja ko hi".split(" ")
		# langs = "".split(" ")
		
		for lang in langs:
			d1 = {}
			for t in a:
				try:
					text = translateText(t, lang)
					d1[t] = text
				except AttributeError:
					d1[t] = ""
			print(f"{d1},")
			
			
	getWordsDict()