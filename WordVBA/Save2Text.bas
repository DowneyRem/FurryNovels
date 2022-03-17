Sub 另存为TXT()
Dim file As String
Dim filename As String


    '更新域
    Selection.WholeStory
    Selection.Fields.Update
    
    
    '保存一次文件
    ActiveDocument.Save
    file = ActiveDocument.FullName
    
    
    '编辑字数统计，表格转文字
    Selection.EndKey Unit:=wdStory
    Selection.MoveUp Unit:=wdLine, Count:=3, Extend:=wdExtend
    Selection.Rows.ConvertToText Separator:=wdSeparateByTabs, NestedTables:=True
    Selection.Style = ActiveDocument.Styles("正文")

    
    '获取文件名，保存TXT/UTF8
    filename = ActiveDocument.Paragraphs(1).Range.Text
    filename = Left(filename, Len(filename) - 1) & ".txt"
    ChangeFileOpenDirectory "C:\Users\Administrator\Desktop\"
    ActiveDocument.SaveAs2 filename:=filename, FileFormat:=wdFormatText, Encoding:=65001
    
    
    '关闭TXT文档，打开DOCX文档
    ActiveDocument.Close 0
    Documents.Open filename:=file
    
    
    '编辑内容字数统计，文字转表格
    Selection.EndKey Unit:=wdStory
    Selection.MoveUp Unit:=wdLine, Count:=3, Extend:=wdExtend
    
    Selection.ConvertToTable Separator:=wdSeparateByTabs, NumColumns:=2, NumRows:=3
    With Selection.Tables(1)
        .Style = "网格型"
        .ApplyStyleHeadingRows = True
        .ApplyStyleLastRow = False
        .ApplyStyleFirstColumn = True
        .ApplyStyleLastColumn = False
    End With
    Selection.Tables(1).AutoFitBehavior (wdAutoFitContent)
    
    
    '保存文件
    ActiveDocument.Save


End Sub
