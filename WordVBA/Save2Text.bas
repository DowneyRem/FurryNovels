Sub 另存为TXT()
Dim DocxPath As String
Dim TextPath As String
Dim Desktop As String
Desktop = "D:\Users\Administrator\Desktop\"


' 常见编码对应编号
' GB 2312   936
' GB18030 54936
' BIG5      950
' UTF8    65001


    '更新域
    Selection.WholeStory
    Selection.Fields.Update

    
    '获取文件路径，保存为TXT/UTF8
    DocxPath = ActiveDocument.FullName
    TextPath = ActiveDocument.Paragraphs(1).Range.Text
    TextPath = Left(TextPath, Len(TextPath) - 1) & ".txt"
    TextPath = Desktop & TextPath
    
    ChangeFileOpenDirectory Desktop
    ActiveDocument.SaveAs2 filename:=TextPath, FileFormat:=wdFormatText, Encoding:=65001, _
        AddToRecentFiles:=False, AllowSubstitutions:=False, LineEnding:=wdCRLF
    
    
    '在Word中关闭TXT文档，打开DOCX文档并保存
    ActiveDocument.Close 0
    Documents.Open TextPath:=DocxPath
    ActiveDocument.Save
    
    
    '打开TXT文件
    Shell ("notepad " & TextPath)


End Sub


