#!/usr/bin/python
# -*- coding: UTF-8 -*-
# import os
import os
from docx.api import Document
from docx.oxml.ns import qn  # 设置字体
from docx.shared import Pt, Cm, Inches  # 设置大小
from docx.shared import RGBColor  # 设置颜色
from docx.enum.style import WD_STYLE
from docx.enum.style import WD_STYLE_TYPE  # 自定样式
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT  # 对齐方式

# 新建文件
document = Document()

latent_styles = document.styles.latent_styles
# print(len(latent_styles))
latent_style_names = [ls.name for ls in latent_styles]
# print(latent_style_names)
latent_styles.default_to_locked = False
latent_styles.default_to_unhide_when_used = False
latent_style = latent_styles.add_latent_style("NORMAL INDENT")
latent_style.hidden = False
latent_style.priority = 2
latent_style.quick_style = True
#就算你启用了正文缩进，也无法在python docx 里直接使用

try:
	path = os.path.join(os.getcwd(),"1.docx")
	document.save(path)
	print("【文件已经写入】")
except:
	print("【文件写入失败】")
