#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
from platform import platform

from pygtrans import Translate

from FileOperate import openTextLines, saveText, formatFileName

if "Windows" in platform():
	client = Translate(proxies={'https': 'http://localhost:10808'})
elif "Linux" in platform():
	client = Translate()


def getLang(text):  # 添加语言标签
	tags = ""
	list1 = "边 变 并 从 点 东 对 发 该 个 给 关 过 还 后 欢 会 机 几 间 见 将 进 经 觉 开 来 里 两 吗 么 没 们 难 让 时 实 说 虽 为 问 无 现 样 应 于 与 则 这 种".split(" ")
	list2 = "邊 變 並 從 點 東 對 發 該 個 給 關 過 還 後 歡 會 機 幾 間 見 將 進 經 覺 開 來 裡 兩 嗎 麼 沒 們 難 讓 時 實 說 雖 為 問 無 現 樣 應 於 與 則 這 種".split(" ")
	list3 = "あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の は ひ ふ へ ほ ま み む め も や ゆ よ ら り る れ ろ わ を ん ぁ ぃ ぅ ぇ ぉ".split(" ")
	list4 = "a b c d e f g h I j k l m n o p q r s t u v w x y z".split(" ")
	
	def countChar(list):
		textnum = len(text)
		j = 0
		for i in range(len(list)):
			char = list[i]
			num = text.count(char)
			if 20000 * num / textnum >= 10:
				j += 1
		# print(j)
		return j
	
	if countChar(list3) >= 0.4 * len(list3):
		tags += "ja"
	elif countChar(list2) >= 0.4 * len(list2):
		tags += "zh_tw"
	elif countChar(list1) >= 0.4 * len(list1):
		tags += "zh_cn"
	elif countChar(list4) >= 0.6 * len(list4):
		tags += "en"
	# print(tags)
	return tags


def getLanguage(text):  # 添加语言标签
	language = client.detect(text).language
	if "zh" in language or "en" in language:
		language = getLang(text)
	if not language:
		language = "en"
	# print(language)
	return language


def translateText(textlist: list, lang) -> list:
	if type(textlist) == str:
		textlist = [textlist]
	texts = client.translate(textlist, lang)
	li = []
	for text in texts:
		li.append(text.translatedText)
	return li


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
				info += translateText(t[0] + "： ", lang)[0] + t[-1] + "\n"
	
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
	
	name2 = translateText(name1, lang)[0]  # 翻译
	name2 = formatFileName(name2).strip()
	textlist = translateText(textlist, lang)
	text = formatText(textlist, lang)
	# print(text, lang1, lang, sep="\n")

	path = os.path.join(os.getcwd(), "Novels", "翻译", f"{name2}.txt")
	saveText(path, text)
	print(f"【{name1}】已翻译", path, sep="\n")
	return path, lang1


if __name__=="__main__":
	path = r"D:\Download\Github\FurryNovelsBot\Novels\《大学教授阿诺雷德》.txt"
	translateFile(path, lang="en")
	pass
