#!/usr/bin/python
# -*- coding: UTF-8 -*-
from functools import cmp_to_key
from DictNovel import tagdict, cmp1
from DictText import textdict, cmp2
from FileOperate import *
from GetTags import getTags

from opencc import OpenCC
cc1 = OpenCC('tw2sp')  #繁转简
cc2 = OpenCC('s2twp')  #簡轉繁


def set2Text(set):
	text = str(set)
	text = text.replace("{'", "")
	text = text.replace("'}", "")
	text = text.replace("', '", " ")
	text = text.replace(" ", "\n")
	return text

	
def sortTags(set, cmp):  # 按dict内顺序对转换后的标签排序
	text = ""
	li = list(set)
	li.sort(key=cmp_to_key(cmp))
	for i in range(len(li)):
		tag = li[i]
		text += "#" + tag + " "
	return text
	
	
def addTags(text): #添加靠谱的标签
	list1 = "邊 變 並 從 點 東 對 發 該 個 給 關 過 還 後 歡 會 機 幾 間 見 將 進 經 覺 開 來 裡 兩 嗎 麼 沒 們 難 讓 時 實 說 雖 為 問 無 現 樣 應 於 與 則 這 種".split(" ")
	list2 = "边 变 并 从 点 东 对 发 该 个 给 关 过 还 后 欢 会 机 几 间 见 将 进 经 觉 开 来 里 两 吗 么 没 们 难 让 时 实 说 虽 为 问 无 现 样 应 于 与 则 这 种".split(" ")
	#语料库来自 https://elearning.ling.sinica.edu.tw/cwordfreq.html
	#从中选取前三百的繁体字部分，并在文章中随机检验，取存在率最高的前50个繁体字符
	
	tags = "" ; j = 0 ; list3 = []
	for i in range(len(list1)):
		char = list1[i]
		num = text.count(char)
		if num >= 5 :
			j += 1
			list3.append(char)
			
	s1 = set(list1)
	s2 = set(list3)
	s = s1.difference(s2)
	chars = set2Text(s)
	k = len(list1) - j
	
	tags += " #txt #finished "
	if j >= 0.2 * len(list1):
		tags += "#zh_tw"
		# print(k)  # 不存在的繁体字符数
		# print(s)   #不存在的繁体字符
	else:
		tags += "#zh_cn"
		if s2 !=set():
			print(s2)  # 存在的繁体字符
	return tags, chars


def translateTags(taglist):  # 获取英文标签
	tags2 = "" ; s = set()
	for i in range(0, len(taglist)):
		tag = taglist[i]
		tag = tag.replace("#", "")
		tag = tag.replace(" ", "")
		tag = tag.replace("　", "")
		tag = tagdict.get(tag)  #获取英文标签
		
		if tag != None:
			s.add(tag)  # 获取到的标签利用set去重
		else:
			tag = taglist[i]
			tags2 += tag + " "
	tags1 = sortTags(s, cmp1)  #对转换后的标签排序
	return tags1, tags2
	

def textFormat(textlist, newtags):
	name = cc2.convert(textlist[0]) + "\n"
	authro = textlist[1].replace("作者：", "")
	authro = "by #" + authro + "\n"
	
	url = textlist[2].replace("网址：", "")
	url = url.replace("網址：", "")
	url = url.replace("链接：", "")
	url = url + "\n"
	
	tags = textlist[3].replace("标签：", "")
	tags = tags.replace("標簽：", "")
	tags += newtags  #新增 #zh_tw 或 #zh_cn
	tags = cc1.convert(tags)  #转简体，只处理简体标签
	list = tags.split()
	(tags1, tags2) = translateTags(list)  #获取已翻译/未翻译的标签
	
	text = name + authro + tags1 + "\n特殊：" + tags2 + "\n" + url #+ "\n"
	print(text)   #格式化输出
	return tags2  #输出不支持的标签


def printTags(path):
	pathlist = findFile(path, ".docx", ".txt")
	dirstr = monthNow()  # 只处理本月的文件
	s = set() ; j = 0 ; chars =""
	for i in range(0, len(pathlist)):
		path = pathlist[i]
		(dir, name) = os.path.split(path)
		(name, ext) = os.path.splitext(name)
		if dirstr in dir:  # 只处理本月的文件
			j += 1
			if ext == ".docx":
				textlist = openDocx4(path)
				text     = openDocx (path)
			elif ext == ".txt":
				textlist = openText4(path)
				text     = openText (path)
				
			if j >= 0:  #无用的if语句，保持上下几行缩进一致
				newtags, char = addTags(text)  #根据本文繁简添加标签
				chars += char +"\n"*1
				s.add(textFormat(textlist, newtags))
				text = cc1.convert(text)       #转简体，只处理简体标签
				getTags(text)
	
	
	if j != 0:
		openNowDir()
		# text = set2Text(s)
		# saveTextDesktop("tags.txt", text)
		# saveTextDesktop("文字.txt", chars)
	else:
		print("本月 " + dirstr + " 无新文档")
	
	
def main():
	print("本月文档如下：")
	print("\n"*2)
	printTags(path)
	
	
if __name__ == "__main__":
	path = os.path.join(os.getcwd())
	path = path.replace("\工具", "")
	pathlist = []
	main()
