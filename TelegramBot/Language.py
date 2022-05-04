#!/usr/bin/python
# -*- coding: UTF-8 -*-


def getLanguage(text):  # 添加语言标签
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
			if 20000*num/textnum >= 10:
				j += 1
		return j
	
	
	if   countChar(list3) >= 0.6 * len(list3):
		tags += "#ja"
	elif countChar(list2) >= 0.6 * len(list2):
		tags += "#zh_tw"
	elif countChar(list1) >= 0.6 * len(list1):
		tags += "#zh_cn"
	elif countChar(list4) >= 0.6 * len(list4):
		tags += "#en"
	# print(tags)
	return tags


if __name__ == "__main__":
	pass
