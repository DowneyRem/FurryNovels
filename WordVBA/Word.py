#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from win32com.client import DispatchEx


def saveDocx(path, text):
	word = DispatchEx('Word.Application')  # 独立进程
	word.Visible = 1  # 0为后台运行
	word.DisplayAlerts = 0  # 不显示，不警告
	template = "D:\\Users\\Administrator\\Documents\\自定义 Office 模板\\小说.dotm"
	docx = word.Documents.Add(template)  # 创建新的word文档
	
	s = word.Selection
	s.Text = text  # 写入文本
	docx.Application.Run("小说排版")  # 运行宏
	
	# 保存文档并退出word
	name = os.path.split(path)[1]
	docx.SaveAs2(path, 16)
	print("【" + name + "】已保存")
	docx.Close(True)
	word.Quit()
