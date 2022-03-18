#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from FileOperate import findFile, openDocx, saveText, removeFile
from opencc import OpenCC
cc1 = OpenCC('tw2sp')  #繁转简
cc2 = OpenCC('s2twp')  #簡轉繁


def getPath(path):
	path0 = path.replace("\小说推荐", "\兽人小说\小说推荐\频道版")
	path0 = path0.replace(".docx", ".txt")
	
	dirandfile = path0.replace(sharepath + "\频道版", "")
	path1 = os.path.join(sharepath + "\简体版" + cc1.convert(dirandfile))  # 简体目录
	path2 = os.path.join(sharepath + "\繁體版" + cc2.convert(dirandfile))  # 繁体目录
	
	(filepath, name) = os.path.split(path)  # 分离文件名和目录名
	name = name.replace(".docx", "")
	return path0, path1, path2, name


def translateText(text, path1, path2):
	list1 = "邊 變 並 從 點 東 對 發 該 個 給 關 過 還 後 歡 會 機 幾 間 見 將 進 經 覺 開 來 裡 兩 嗎 麼 沒 們 難 讓 時 實 說 雖 為 問 無 現 樣 應 於 與 則 這 種".split(" ")
	list2 = "边 变 并 从 点 东 对 发 该 个 给 关 过 还 后 欢 会 机 几 间 见 将 进 经 觉 开 来 里 两 吗 么 没 们 难 让 时 实 说 虽 为 问 无 现 样 应 于 与 则 这 种".split(" ")
	
	j = 0
	for i in range(len(list1)):
		char = list1[i]
		num = text.count(char)
		if num >= 5:
			j += 1
	
	if j >= 0.2 * len(list1):
		text1 = cc1.convert(text)  # 繁体文件，转简体
		saveText(path2, text)      # 复制后，存繁体目录
		saveText(path1, text1)     # 转简体，存简体目录
	else:
		text2 = cc2.convert(text)  # 简体文件，转繁体
		saveText(path1, text)      # 复制后，存简体目录
		saveText(path2, text2)     # 转繁体，存繁体目录


def convert(path):
	list = findFile(path, ".docx")
	for i in range(0, len(list)):
		path = list[i]
		(path0, path1, path2, name) = getPath(path)
		if os.path.exists(path0):
			i += 1
			print("【" + name + "】在本次运行前已转换")
		else:
			text = openDocx(path)
			saveText(path0, text)  # 不区分繁简，存频道目录
			translateText(text, path1, path2)
			print("【"+ name +"】转换成功，当前进度：" + str(round(100*(i+1)/len(list),2))+"%")


def main():
	print("是否要【删除旧文件】重新转换？")
	string = input("输入【 1 】即【删除旧文件】"+"\n"*2)
	if str(1) in string:
		removeFile(sharepath)
		print("【删除】旧文件")
	else:
		print("【保留】旧文件")
		
	print("文档转换开始：")
	print("-"*40)
	convert(path)
	print("-"*40)
	print("文档转换已完成")
	os.system("python ./PrintTags.py")
	os.system("pause")
	
	
if __name__ == "__main__":
	path = os.getcwd()
	path = path.replace("\工具","")
	sharepath = path.replace("\小说推荐", "\兽人小说\小说推荐")
	main()
