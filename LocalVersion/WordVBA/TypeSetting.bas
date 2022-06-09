Sub 小说排版()
Dim filename As String
Dim Para2 As String


'
' 小说排版 宏
'
    
    
    '基本文本插入
    '没有则在第一行后插入下面的内容
    Para2 = ActiveDocument.Paragraphs(2).Range.Text
    If InStr(1, Para2, "作者", vbTextCompare) = 0 Then
    
        Selection.HomeKey Unit:=wdStory
        Selection.MoveDown Unit:=wdLine, Count:=1, Extend:=wdMove
        Selection.TypeText Text:="作者："
        Selection.TypeParagraph
        Selection.TypeText Text:="网址："
        Selection.TypeParagraph
        Selection.TypeText Text:="标签："
        Selection.TypeParagraph
        Selection.TypeText Text:=""
        Selection.TypeParagraph
        Selection.TypeText Text:=""
        Selection.TypeParagraph
    
    End If
    
    
    
    '基本格式设置1
    '全文设置成正文缩进的格式
    Selection.WholeStory
    Selection.Style = ActiveDocument.Styles("正文缩进")
    
    
    '英文符号替换
    '逗号
    'Selection.Find.ClearFormatting
    'Selection.Find.Replacement.ClearFormatting
    'Selection.Find.Replacement.Style = ActiveDocument.Styles("正文缩进")
    'With Selection.Find
    '    .Text = ","
    '    .Replacement.Text = "，"
    '    .Forward = True
    '    .Wrap = wdFindContinue
    '    .Format = True
    '    .MatchWildcards = True
    'End With
    'Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '引号替换1
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("正文缩进")
    With Selection.Find
        .Text = "^13"""
        .Replacement.Text = "^13“"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '引号替换2
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("正文缩进")
    With Selection.Find
        .Text = "([，,。,？,！])"""
        .Replacement.Text = "\1”"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '省略号替换
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("正文缩进")
    With Selection.Find
        .Text = ".{3,}"
        .Replacement.Text = "……"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("正文缩进")
    With Selection.Find
        .Text = "。{3,}"
        .Replacement.Text = "……"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    
    '全角空格替换为空
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "　"
        .Replacement.Text = ""
        .Forward = True
        .Wrap = wdFindContinue
        .MatchByte = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '制表符转替换为空
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^t"
        .Replacement.Text = ""
        .Forward = True
        .Wrap = wdFindContinue
        .MatchByte = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '2个半角空格替换为空
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "  "
        .Replacement.Text = ""
        .Forward = True
        .Wrap = wdFindContinue
        .MatchByte = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '段尾半角空格替换为空
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = " ^13"
        .Replacement.Text = "^13"
        .Forward = True
        .Wrap = wdFindContinue
        .MatchByte = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '手动换行符转换行符
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^l"
        .Replacement.Text = "^13"
        .Forward = True
        .Wrap = wdFindContinue
        .MatchByte = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    
    '去除过多空行
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^p^p"
        .Replacement.Text = "^p"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchWildcards = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    
    '——————分割线转空行
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "—{3,20}"
        .Replacement.Text = "^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '------------分割线转空行
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "-{2,20}"
        .Replacement.Text = "^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    
    
    '中文数字转标题
    '十以内中文数字
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^13([零,〇,一,二,三,四,五,六,七,八,九,十])^13"
        .Replacement.Text = "^13^13第\1章^13^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '二十以内中文数字
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^13(十[一,二,三,四,五,六,七,八,九]十)^13"
        .Replacement.Text = "^13^13第\1章^13^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '整十中文数字
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^13([二,三,四,五,六,七,八,九]十)^13"
        .Replacement.Text = "^13^13第\1章^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '一百以内中文数字
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^13([二,三,四,五,六,七,八,九]十[一,二,三,四,五,六,七,八,九])^13"
        .Replacement.Text = "^13^13第\1章^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
        
    '统一插入空行
    '在二级标题（第X章）前插入两个空行
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "(第?[章,卷]*)"
        .Replacement.Text = "^13^13\1^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "(第??[章,卷]*)"
        .Replacement.Text = "^13^13\1^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "(第??[章,卷]*)"
        .Replacement.Text = "^13\1^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "(第???章*)"
        .Replacement.Text = "^13^13\1^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '汉字【第一千章】前，插入空行
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "(第?????章*)"
        .Replacement.Text = "^13^13\1^13^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '前言后记等插入空行
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "(前言*^13)"
        .Replacement.Text = "^13^13\1^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
            
        
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "(番外*^13)"
        .Replacement.Text = "^13^13\1^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
            
            
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "(后记*^13)"
        .Replacement.Text = "^13^13\1^13"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "(作者的话*)^13"
        .Replacement.Text = "^13^13\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    
    '统一设置标题
    '设置一级标题：第X卷
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 1")
    With Selection.Find
        .Text = "(第?卷*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '设置二级标题：第X章
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(第?章*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '第9.5章，设置标题
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(第[0-9]@.[0-9]章*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    '中文序号，设置标题
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(第?章*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(第??章*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
        
    '十几章，整十章节补
    'Selection.Find.ClearFormatting
    'Selection.Find.Replacement.ClearFormatting
    'Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    'With Selection.Find
    '    .Text = "(第??章)"
    '    .Replacement.Text = "\1"
    '    .Forward = True
    '    .Wrap = wdFindContinue
    '    .Format = True
   '     .MatchWildcards = True
    'End With
    Selection.Find.Execute Replace:=wdReplaceAll
        
        
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(第???章*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(第????章*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    
    '前言后记等设置标题
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(前言*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
        
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(序)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
            
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(后记*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
            
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    Selection.Find.Replacement.Style = ActiveDocument.Styles("标题 2")
    With Selection.Find
        .Text = "(作者的话*)^13"
        .Replacement.Text = "\1"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = True
        .MatchWildcards = True
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    
    '基本格式设置2
    '去除多余的空行
    Selection.Find.ClearFormatting
    Selection.Find.Replacement.ClearFormatting
    With Selection.Find
        .Text = "^p^p^p"
        .Replacement.Text = "^p"
        .Forward = True
        .Wrap = wdFindContinue
        .Format = False
        .MatchCase = False
        .MatchWholeWord = False
        .MatchByte = False
        .MatchAllWordForms = False
        .MatchSoundsLike = False
        .MatchWildcards = False
        .MatchFuzzy = False
    End With
    Selection.Find.Execute Replace:=wdReplaceAll
    
    
    
    '前5行设置成正文样式
    Selection.HomeKey Unit:=wdStory
    Selection.MoveDown Unit:=wdLine, Count:=6, Extend:=wdExtend
    Selection.Style = ActiveDocument.Styles("正文")
    
    
    '第一行设置成标题样式
    Selection.HomeKey Unit:=wdStory
    Selection.MoveDown Unit:=wdLine, Count:=1, Extend:=wdExtend
    Selection.Style = ActiveDocument.Styles("标题")
    
    
    '最后一行表格设置格式
    Selection.EndKey Unit:=wdLine
    Selection.EndKey Unit:=wdStory
    Selection.Style = ActiveDocument.Styles("正文")
    Selection.MoveUp Unit:=wdLine, Count:=1, Extend:=wdExtend
    Selection.Style = ActiveDocument.Styles("正文")
    
    
    '删除字数统计最后一行表格设置格式
    Para = Selection.Range.Text
    If InStr(1, Para2, "字数", vbTextCompare) = 0 Then
    
        Selection.EndKey Unit:=wdLine
        Selection.EndKey Unit:=wdStory
        Selection.MoveUp Unit:=wdLine, Count:=2, Extend:=wdExtend
        Selection.Delete
        
    End If
    


    '更新域
    Selection.WholeStory
    Selection.Fields.Update
    'ActiveDocument.Save
    
    
    '获取文件名，桌面保存DOCX
    'ActiveDocument.Save
    'filename = ActiveDocument.Paragraphs(1).Range.Text
    'filename = Left(filename, Len(filename) - 1) & ".docx"
    'ChangeFileOpenDirectory "D:\Users\Administrator\Desktop\"
    'ActiveDocument.SaveAs2 filename:=filename
    
    
    '获取文件名，保存TXT
    'filename = ActiveDocument.Paragraphs(1).Range.Text
    'filename = Left(filename, Len(filename) - 1) & ".txt"
    'ChangeFileOpenDirectory "D:\Users\Administrator\Desktop\"
    'ActiveDocument.SaveAs2 filename:=filename, FileFormat:=wdFormatText
    
    
    '关闭文件
    'ActiveDocument.Close 0
    
    
    
End Sub



