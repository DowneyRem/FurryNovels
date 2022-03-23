#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from FileOperate import saveText

# 适用于文本的标签关键词
# key为关键词，value为对应标签，
# 关键词——标签可以一对多
# 正文标签
textdict = {
	"sfw":"SFW",
	"R-18":"R18",
	"R18":"R18",
	"R-18G":"R18G",
	"R18G":"R18G",
	"BL":"Gay",
	"腐向け":"Gay",
	"腐向":"Gay",
	"同志":"Gay",
	"男同性恋":"Gay",
	"GL":"Lesbian",
	"百合":"Lesbian",
	"女同性恋":"Lesbian",
	"BG":"General",
	"男女":"General",
	"科幻":"ScienceFiction",
	"奇幻":"Fantasy",
	"魔幻":"Fantasy",
	"喜剧":"Comedy",
	"悲剧":"Tragedy",
	

	
	"龙根":"dragon R18",
	"龙棒":"dragon R18",
	

	
	"阴道交":"VaginalSex",
	"阴交":"VaginalSex",
	"阴道":"VaginalSex",
	"肛交":"Anal",
	"后入":"Anal",
	"口交":"BlowJob",
	"生殖腔":"Cloaca",
	"生殖缝":"Cloaca",
	"泄殖腔":"Cloaca",
	"尾交":"TailJob",
	"自慰":"Masturbation",
	"翼交":"WingJob",
	"拳交":"Fisting",
	"足交":"FootJob",
	"脚爪":"Paw",
	"爪子":"Paw",
	"足控":"Paw",
	"舔足":"Paw",
	"袜交":"SockJob",
	"手淫":"HandJob",
	"脑交":"BrainFuck",
	"耳交":"EarFuck",
	"阴茎打脸":"CockSlapping",
	"阴茎摩擦":"Frottage",
	"尿道插入":"UrethraInsertion",
	"奸杀":"RapedWhileDying",
	"搔痒":"tickling",
	"挠痒":"tickling",
	
	"强奸":"Rape",
	"乱伦":"Incest",
	"群交":"Group",
	"群p":"Group",
	"轮奸":"Group",
	"绿帽":"Cuckold",
	"父子丼":"Oyakodon",
	"父子":"Oyakodon",
	"兄弟丼":"brother",
	"兄弟":"brother",
	
	"调教":"BDSM",
	"bdsm":"BDSM",
	"捆绑":"Bondage",
	"束缚":"Bondage",
	"电击":"ElectricShocks",
	"精神控制":"MindControl",
	"精控":"MindControl",
	"洗脑":"MindControl",
	"窒息":"Asphyxiation",
	"高潮禁止":"OrgasmDenial",
	"禁止高潮":"OrgasmDenial",
	"射精控制":"OrgasmDenial",
	"控制射精":"OrgasmDenial",
	"主奴":"Slave",
	"性奴":"Slave",
	"主仆":"Slave",
	"鼻吊钩":"NoseHook",
	"鼻环":"NoseHook",
	"狗链":"Leash",
	"穿孔":"Piercing",
	"纹身":"Tattoo",
	"淫纹":"CrotchTattoo",
	"肉便器":"PublicUse",
	"rbq":"PublicUse",
	"RBQ":"PublicUse",
	"饮尿":"PissDrinking",
	"圣水":"PissDrinking",
	"食粪":"Coprophagia",
	"黄金":"Coprophagia",
	"人体家具":"Forniphilia",
	"人体餐盒":"FoodOnBody",
	"育肥":"WeightGain",
	"肥满化":"WeightGain",
	"战损":"BattleDamage",
	"欠損":"BattleDamage",
	"虐屌":"CBT",
	"cbt":"CBT",
	"虐腹":"GutTorture",
	"身体改造":"BodyModification",
	"肉体改造":"BodyModification",
	"变身":"Transformation",
	"兽化":"Transfur",
	"同化":"Transfur",
	"龙化":"Transfur",
	"TF":"Transfur",
	"附身":"Possession",
	"寄生":"Parasite",
	"石化":"Petrification",
	"堕落":"corruption",
	"恶堕":"corruption",
	"雌堕":"FemaleCorruption",
	"催眠":"Hypnosis",
	"雄臭":"Smell",
	"臭脚":"Smell",
	"迷药":"Chloroform",
	"下药":"Chloroform",
	"药物":"Drugs",
	"酗酒":"Drunk",
	"寻欢洞":"GloryHole",
	"摄像":"Filming",
	"性转":"GenderBender",
	"灵魂交换":"BodySwap",
	"身体交换":"BodySwap",
	"机械奸":"Machine",
	"drone":"Drone",
	"尿布":"Diaper",
	
	"乳胶衣":"Latex",
	"胶衣":"Latex",
	"乳胶":"Latex",
	"latex":"Latex",
	"胶液":"Rubber",
	"胶":"Rubber",
	"龙胶":"Rubber",
	"rubber":"Rubber",
	"生物衣":"LivingClothes",
	"防毒面具":"GasMusk",
	"盔甲":"Armor",
	"骑士盔甲":"MetalArmor",
	"动力装甲":"PowerArmor",
	"军装":"Military",
	"紧身衣":"Leotard",
	"拘束衣":"StraitJacket",
	"泳装":"SwimSuit",
	"六尺褌":"Fundoshi",
	"袜子":"socks",
	
	"肌肉":"Muscles",
	"筋肉":"Muscles",
	"巨根":"Hyper",
	"巨大化":"Macro",
	"包茎":"Phimosis",
	"吞食":"Vore",
	"丸吞":"Vore",
	"阴茎吞噬":"CockPhagia",
	"肛门吞食":"AnalPhagia",
	"尾巴吞食":"TailPhagia",
	"出产":"Birth",
	"生产":"Birth",
	"产卵":"Eggs",
	"阴茎出产":"PenisBirth",
	"肛门出产":"AnalBirth",
	
	}


def cmp2(a, b):  # 按dict内部顺序进行排序
	def getindex(a):
		try:
			li = list(textdict.values())
			index = li.index(a)
		except:
			li = list(textdict.keys())
			index = li.index(a)
		return index
	
	a = getindex(a)
	b = getindex(b)
	if a > b:
		return 1
	elif a < b:
		return -1
	else:
		return 0
	
	
def saveDict2Md(dict, name):
	text = "### 关键词标签表\n"
	text = text + "\n| 标签 | 关键词 | "
	text = text + "\n| -- | -- | "
	list1 = list(textdict.items())
	for i in range(0, len(list1)):
		(key, value) = list1[i]
		if value != "":
			value = "#" + value
			text += "\n| " + value + " | " + key + " |"
	
	path = os.path.join(os.getcwd(), name + ".md")
	saveText(path, text)


if __name__ == '__main__':
	saveDict2Md(textdict, "TextTags")
	# saveDict2Md(racedict, "RaceTags")
