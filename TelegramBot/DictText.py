#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 正文关键词对应标签
# key为关键词，value为对应标签
# 关键词——标签可以一对多


text = {
	"同志": "Gay",
	"男同性恋": "Gay",
	"男同": "Gay",
	"百合": "Lesbian",
	"女同性恋": "Lesbian",
	"女同": "Lesbian",
	"科幻": "ScienceFiction",
	"奇幻": "Fantasy",
	"魔幻": "Fantasy",
	"喜剧": "Comedy",
	"悲剧": "Tragedy",
	
	"阴道交": "VaginalSex",
	"阴交": "VaginalSex",
	"阴道": "VaginalSex",
	"肛交": "Anal",
	"后入": "Anal",
	"口交": "BlowJob",
	"生殖腔": "Cloaca",
	"生殖缝": "Cloaca",
	"泄殖腔": "Cloaca",
	"尾交": "TailJob",
	"自慰": "Masturbation",
	"翼交": "WingJob",
	"拳交": "Fisting",
	"足交": "FootJob",
	"脚爪": "Paw",
	"爪子": "Paw",
	"足控": "Paw",
	"舔足": "Paw",
	"袜交": "SockJob",
	"手淫": "HandJob",
	"脑交": "BrainFuck",
	"耳交": "EarFuck",
	"阴茎打脸": "CockSlapping",
	"阴茎摩擦": "Frottage",
	"尿道插入": "UrethraInsertion",
	"奸杀": "RapedWhileDying",
	"搔痒": "tickling",
	"挠痒": "tickling",
	
	"强奸": "Rape",
	"乱伦": "Incest",
	"群交": "Group",
	"群p": "Group",
	"轮奸": "Group",
	"绿帽": "Cuckold",
	"父子丼": "Oyakodon",
	"父子": "Oyakodon",
	"兄弟丼": "brother",
	"兄弟": "brother",
	
	"调教": "BDSM",
	"bdsm": "BDSM",
	"捆绑": "Bondage",
	"束缚": "Bondage",
	"电击": "ElectricShocks",
	"精神控制": "MindControl",
	"精控": "MindControl",
	"洗脑": "MindControl",
	"窒息": "Asphyxiation",
	"高潮禁止": "OrgasmDenial",
	"禁止高潮": "OrgasmDenial",
	"射精控制": "OrgasmDenial",
	"控制射精": "OrgasmDenial",
	"主奴": "Slave",
	"性奴": "Slave",
	"主仆": "Slave",
	"鼻吊钩": "NoseHook",
	"鼻环": "NoseHook",
	"狗链": "Leash",
	"穿孔": "Piercing",
	"纹身": "Tattoo",
	"淫纹": "CrotchTattoo",
	"肉便器": "PublicUse",
	"rbq": "PublicUse",
	"RBQ": "PublicUse",
	"饮尿": "PissDrinking",
	"圣水": "PissDrinking",
	"食粪": "Coprophagia",
	"黄金": "Coprophagia",
	"人体家具": "Forniphilia",
	"人体餐盒": "FoodOnBody",
	"育肥": "WeightGain",
	"肥满化": "WeightGain",
	"战损": "BattleDamage",
	"欠損": "BattleDamage",
	"虐屌": "CBT",
	"cbt": "CBT",
	"虐腹": "GutTorture",
	"身体改造": "BodyModification",
	"肉体改造": "BodyModification",
	"变身": "Transformation",
	"兽化": "Transfur",
	"同化": "Transfur",
	"龙化": "Transfur",
	"TF": "Transfur",
	"附身": "Possession",
	"寄生": "Parasite",
	"石化": "Petrification",
	"堕落": "corruption",
	"恶堕": "corruption",
	"雌堕": "FemaleCorruption",
	"催眠": "Hypnosis",
	"雄臭": "Smell",
	"臭脚": "Smell",
	"迷药": "Chloroform",
	"下药": "Chloroform",
	"药物": "Drugs",
	"酗酒": "Drunk",
	"寻欢洞": "GloryHole",
	"摄像": "Filming",
	"性转": "GenderBender",
	"灵魂交换": "BodySwap",
	"身体交换": "BodySwap",
	"机械奸": "Machine",
	"drone": "Drone",
	"尿布": "Diaper",
	
	"乳胶衣": "Latex",
	"胶衣": "Latex",
	"乳胶": "Latex",
	"latex": "Latex",
	"胶液": "Rubber",
	"胶": "Rubber",
	"龙胶": "Rubber",
	"rubber": "Rubber",
	"生物衣": "LivingClothes",
	"防毒面具": "GasMusk",
	"盔甲": "Armor",
	"骑士盔甲": "MetalArmor",
	"动力装甲": "PowerArmor",
	"军装": "Military",
	"紧身衣": "Leotard",
	"拘束衣": "StraitJacket",
	"泳装": "SwimSuit",
	"六尺褌": "Fundoshi",
	"袜子": "Socks",
	
	"肌肉": "Muscles",
	"筋肉": "Muscles",
	"巨根": "Hyper",
	"巨大化": "Macro",
	"包茎": "Phimosis",
	"吞食": "Vore",
	"吞噬": "Vore",
	"丸吞": "Vore",
	"阴茎吞噬": "CockVore",
	"肛门吞食": "AnalVore",
	"尾巴吞食": "TailVore",
	
	"生产": "Birth",
	"妊娠": "Birth",
	"雄妊娠": "MaleBirth",
	"产卵": "Eggs",
	"阴茎出产": "PenisBirth",
	"肛门出产": "AnalBirth",
	
	"血腥": "R18G Blood",
	"流血": "R18G Blood",
	"Blood": "R18G Blood",
	"断肢": "R18G Mutilation",
	"Mutilation": "R18G Mutilation",
	"阉割": "R18G Castrated",
	"Castrated": "R18G Castrated",
	"性器破坏": "R18G Castrated",
	
	}
# 雄性妊娠与雌性堕落区别？


textdict={}
for i in text:
	l = text[i].split(" ")
	textdict[i] = l


if __name__ == '__main__':
	print(textdict)