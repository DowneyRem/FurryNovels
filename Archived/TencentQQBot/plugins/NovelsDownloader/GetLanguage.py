#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import logging
from locale import getdefaultlocale
from requests.exceptions import SSLError

from pygtrans import Translate

from .configuration import proxy_list


# 设置翻译格式，设置代理
client = Translate(fmt="text", proxies={'https': proxy_list[0]})

local_times, google_times = 0, 0
wordsdict, langs, words = {}, [], []
# langs = "en zh zh_cn zh_tw fr ru ar es de pt ja ko hi".split(" ")
json1 = os.path.join(os.path.dirname(__file__), "data", "translation.json")  # 主用数据文件
json2 = os.path.join(os.path.dirname(__file__), "data", "translated.json")  # 新翻译存放文件


# 判断语言
def getLangCharacter(text: str) -> str:  # 添加语言标签
	lang = ""
	list1 = "边 变 并 从 点 东 对 发 该 个 给 关 过 还 后 欢 会 机 几 间 见 将 进 经 觉 开 来 里 两 吗 么 没 们 难 让 时 实 说 虽 为 问 无 现 样 应 于 与 则 这 种".split(
		" ")
	list2 = "邊 變 並 從 點 東 對 發 該 個 給 關 過 還 後 歡 會 機 幾 間 見 將 進 經 覺 開 來 裡 兩 嗎 麼 沒 們 難 讓 時 實 說 雖 為 問 無 現 樣 應 於 與 則 這 種".split(
		" ")
	list3 = "あ い う え お か き く け こ さ し す せ そ た ち つ て と な に ぬ ね の は ひ ふ へ ほ ま み む め も や ゆ よ ら り る れ ろ わ を ん が ぎ ぐ げ ご ざ じ ず ぜ ぞ だ ぢ づ で ど ぱ ぴ ぷ ぺ ぽ ば び ぶ べ ぼ ぁ ぃ ぅ ぇ ぉ っ ア イ ウ エ オ カ キ ク ケ コ サ シ ス セ ソ タ テ ツ テ ト ナ ニ ヌ ネ ノ ハ ヒ フ ヘ ホ マ ミ ム メ モ ヤ ユ ヨ ラ リ ル レ ロ ワ ヲ ン ガ ギ グ ゲ ゴ ザ ジ ズ ゼ ゾ ダ ヂ ヅ デ ド パ ピ プ ペ ポ バ ビ ブ ベ ボ ァ ィ ゥ ェ ォ ッ".split(
		" ")
	list4 = "하 수 사 우 아 대 그 나 문 생 모 만 경 어 자 다 여 정 보 가 함 지 시 누 세 운 퍼 학 바 무 국 얼 이 방 새 과 특 교 선 예 역 결 내 물 일 중 느 너 의 엄 남 작 상 더 최 환 컴 먼 부 기 거 오 광 민 람 리 니 러 제 각 르 들 떤 신 도 께 간 구 계 동 센 로 엇 굴 번 법 롭 히 육 술 용 론 요 끼 미 마 편 품 황 욱 근 퓨 저 분 업 늘 고 족".split(
		" ")
	
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
		logging.debug(f"{j}, {textnum}, {(1000 * j) / textnum}")
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
		"ko": [0xac00, 0xd7a3],  # 谚文范围
		"ja": [0x3040, 0x30ff],  # 假名范围
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

