#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import logging
from decimal import Decimal
from FileOperate import timethis
# logging.basicConfig(format='%(levelname)s - %(message)s', level=logging.INFO)


dict1 = {
	"shu": {'一': 1, "两": 2, '二': 2, '三': 3, '四': 4, '五': 5,
	        '六': 6, '七': 7, '八': 8, '九': 9, "〇": 0, "零": 0,},
	"wei": {"dian": "点", "shi": "十", "bai": "百",
	        "qian": "千", "wan": "万", "yi" : "亿"}}

dict2 = {
	"shu": {"壹": 1, "贰": 2, "叁": 3, "肆": 4, "伍": 5,
	        "陆": 6, "柒": 7, "捌": 8, "玖": 9, "零": 0, },
	"wei": {"dian": "点", "shi": "拾", "bai": "佰",
	        "qian": "仟", "wan": "萬", "yi" : "億"}}


def transSerial(s:str, numdict:dict=dict1):
	# 序号转换，小数转换半成品
	shu = numdict["shu"]
	j = ""
	for i in s:
		j += str(shu[i])
	return int(j)


# @timethis
def trans(s:str, numdict=dict1) -> int:
	# 万位以下中文数字转换：九千零二十一 -> 9021
	# 参考自：https://segmentfault.com/a/1190000013048884
	
	shu = numdict["shu"]
	wei = numdict["wei"]
	num = 0
	logging.info(s)
	dian, shi, bai, qian, wan, yi = wei["dian"], wei["shi"], wei["bai"], wei["qian"],wei["wan"], wei["yi"]
	dian, shi, bai, qian, wan, yi = s.find(dian), s.find(shi), s.find(bai), s.find(qian),s.rfind(wan), s.rfind(yi)
	
	if wan !=-1 or yi !=-1:
		try:
			raise ValueError("数字过大")
		except ValueError as e:
			print("{}，请使用transBigNum".format(e))
			
	else:
		if qian != -1:
			num += shu[s[qian-1: qian]] * 1000
		if bai != -1:
			num += shu[s[bai-1: bai]] * 100
		if shi != -1:
			shiwei = s[shi-1: shi].replace("零", "")
			num += shu.get(shiwei, 1)*10  #处理十位忽略的一
			
		if dian != -1:
			try:
				num += shu[s[dian-1: dian-0]]
			except KeyError:  # 十
				num += 10
			xiaoshu = s[dian + 1:]
			num += transSerial(xiaoshu)/ 10 ** len(xiaoshu)
		
		elif s[-1] in shu:
			num += shu[s[-1]]
		
		# print(num)
		return num
	
	
def transBigNum(s:str, numdict:dict=dict1) -> int:
	# 万位以上中文数字转换
	# 八千零一万零二百三十亿，零四百万七千八百九十 -> 8001 0230 0400 7890
	# 参考自：https://segmentfault.com/a/1190000013048884
	
	wei = numdict["wei"]
	num = 0
	logging.info(s)
	wan, yi = wei["wan"], wei["yi"]
	wan, yi ,lwan = s.rfind(wan), s.rfind(yi), s.find(wan)
	
	if lwan < yi or yi != -1:  #万亿以上；亿以上
		num += transBigNum(s[: yi]) * 10 ** 8
	if wan != -1 and wan > yi:
		num += trans(s[yi + 1: wan], numdict) * 10 ** 4
	else: wan = yi
	
	if s[wan+1:]:
		num += trans(s[wan + 1:], numdict)
	# print(num)
	return num


@timethis
def transAbbr(s:str, numdict:dict=dict1):
	# 中文缩略数字：一万五，三千四，二百五，三十四，二点五
	shu = numdict["shu"]
	wei = numdict["wei"]
	l = list(wei.values())
	for i in l:
		if s.find(i) != -1:
			power = l.index(i)
			# print(s)
			num = shu[s[0]]*10**power + shu[s[-1]]*10**(power-1)
			# print(num)
			return num


# 写成装饰器？
def Chinese2Arabic(s:str, mode=0) -> int:
	# 亿万以内数字，小数数位无限制
	
	if len(s) == 3:  # 缩略数字：一万五
		num = transAbbr(s)
	elif mode == 0:  # 中文小写数字
		numdict = dict1
		num = transBigNum(s, numdict)
	elif mode == 1:  # 中文大写数字
		numdict = dict2
		num = transBigNum(s, numdict)
	elif mode == 2: # 序号转换
		num = transSerial(s)
	print("{}\n{}".format(s, num))
	return num
	

def test1():
	print(trans('十') == 10)
	print(trans('一百零一') == 101)
	print(trans('九百二十一') == 921)
	print(trans('九千零十一') == 9011)
	print(trans('九千零二十一') == 9021)
	print(trans('五十六万零一十') == 560010)
	print(trans('三点一四一五九二六') == 3.1415926)
	print(trans('三点一') == 3.1)
	print(trans('四万六') == 46000)
	
	print(transBigNum('十') == 10)
	print(transBigNum('一百零一') == 101)
	print(transBigNum('九百二十一') == 921)
	print(transBigNum('九千零二十一') == 9021)
	print(transBigNum('五十六万零一十') == 560010)
	print(transBigNum('五千零十六万零一十') == 50160010) # todo1
	print(transBigNum('五千零一十六万零一十') == 50160010)
	print(transBigNum('五十六亿零一十') == 5600000010)
	print(transBigNum('五十六亿零三百万零一十') == 5603000010)
	print(transBigNum('一万亿零二千一百零一') == 1000000002101)
	print(transBigNum('一万亿二千一百万零一百零一') == 1000021000101)
	print(transBigNum('一万零二百三十亿四千万零七千八百九十') == 1023040007890)
	print(transBigNum('八千零一万零二百三十亿四百万零七千八百九十') == 8001023004007890)

	transSerial("一二三四五")
	transAbbr("五十六")
	Chinese2Arabic("一百三")
	Chinese2Arabic("十七十八")
	Chinese2Arabic("一千二百三十四万五千六百七十八亿一千二百三十四万五千六百七十八")


def Arabic2Chinese(i:float, mode=0) -> str:
	print(i)
	pass


def strSerial(num:float, numdict=dict1) -> str:
	# 序号转换，小数转换半成品
	shu = numdict["shu"]
	wei = numdict["wei"]
	shu = dict(zip(shu.values(), shu.keys()))
	
	text = ""
	for i in str(num):
		try:
			i = shu[int(i)]
		except ValueError:  # 小数点报错
			i = wei["dian"]
		text += i
		
	# print(text)
	return text


def strNum(num: float, numdict=dict1) -> str:
	shu = numdict["shu"]
	wei = numdict["wei"]
	shu = dict(zip(shu.values(), shu.keys()))
	l = list(wei.values())
	
	text = ""
	strnum = str(int(num))
	length = len(strnum)
	if length <= 4:
		for i in range(len(strnum)):
			if shu[int(strnum[i])] != "零":
				j = shu[int(strnum[i])] + l[length - i - 1]
				text += j
			else:
				text += "零"
		
		#去除多个连续占位的零，去除末尾的零
		text = re.sub("零{2,}", "零", text, 1)
		if text.endswith("零"):
			text = text[:-1]
		text = text.replace("点", "")
		
		if num != int(num):  # 小数部分
			decimalnum = Decimal(str(num)) - int(num)
			decimalnum = str(decimalnum)[2:]
			text += wei["dian"] + strSerial(int(decimalnum))
		
		# print(6,num)
		# print(7,text)
		return text


#需要重构，以小数点为界限，每4位向前推进
def strBigNum(num:float, numdict:dict=dict1) -> str:
	
	shu = numdict["shu"]
	wei = numdict["wei"]
	shu = dict(zip(shu.values(), shu.keys()))
	# print(num)
	strnum = str(int(num))
	length = len(strnum)
	# print(length)
	text = ""
	if 12 < length <= 16:
		wanyi = strnum[:4]
		# print(wanyi)
		text += strNum(int(wanyi)) + wei["wan"]
		
		strnun = strnum
		if wei["qian"] in strBigNum(int(strnum)) :
			text += strBigNum(int(strnum))
		else:
			text += shu[0] + strBigNum(int(strnum))
		pass
	
	if 8 < length <= 12:
		yiji = strnum[:4]
		text += strNum(int(yiji)) + wei["yi"]
		strnum = strnum[4:]
		
		if wei["qian"] in strBigNum(int(strnum)) :
			text += strBigNum(int(strnum))
		else:
			text += shu[0] + strBigNum(int(strnum))
	
	#丢了万级的零
	if 4 < length <= 8:
		wanji = strnum[0:4-8+length]
		text += strNum(int(wanji)) + wei["wan"]
		strnum = strnum[4-8+length:]
		text += strBigNum(int(strnum))
		
	if 0 < length <= 4 :
		if wei["qian"] in strNum(int(strnum)):
			text += strNum(int(strnum))
		else:
			text += shu[0] + strNum(int(strnum))
	
	decimalnum = str(num).replace(str(int(num)), "")
	if decimalnum :
		text += strSerial(decimalnum)
	# print(text)
	return text
	
	
def test2():
	print(transBigNum(strBigNum(12))==12)
	# print(transBigNum(strNum(10.34))==10.34)
	# print(transBigNum(strBigNum(100.3))==100.3)
	print(transBigNum(strBigNum(102.3))==102.3)
	print(transBigNum(strBigNum(1023.0506))==1023.0506)
	print(transBigNum(strBigNum(10010101))==10010101)
	print(transBigNum(strBigNum(10100101))==10100101)
	print(transBigNum(strBigNum(200110300101))==200110300101)

	
	
def main():
	# test1()
	test2()
	# print(transBigNum("十七十八"))
	# print(strBigNum(20800100101.1415))
	# strSerial(1310.15)
	# strDecimal(3.)
	# print(trans('二十七十八'))
	

if __name__ == '__main__':
	main()
	pass
