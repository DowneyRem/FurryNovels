Sub 另存为TXT()
Dim DocxPath As String
Dim TextPath As String
Dim Desktop As String
Desktop = CreateObject("WScript.Shell").SpecialFolders("Desktop") & "\"


' 常见编码对应编号
' GB 2312   936
' GB18030 54936
' BIG5      950
' UTF8    65001


    '更新域
    Selection.WholeStory
    Selection.Fields.Update


    ''新增空行
    'Selection.Find.ClearFormatting
    'Selection.Find.Replacement.ClearFormatting
    'With Selection.Find
	'	.Text = "^p"
	'	.Replacement.Text = "^p^p"
	'	.Forward = True
	'	.Wrap = wdFindContinue
	'	.MatchByte = True
    'End With
	'Selection.Find.Execute Replace:=wdReplaceAll

	
    '获取文件路径，在桌面上另存为TXT/UTF8
    DocxPath = ActiveDocument.FullName
    TextPath = ActiveDocument.Paragraphs(1).Range.Text
    TextPath = Left(TextPath, Len(TextPath) - 1) & ".txt"
    TextPath = Desktop & TextPath
    MsgBox (TextPath)
    
    ChangeFileOpenDirectory Desktop
    ActiveDocument.SaveAs2 filename:=TextPath, FileFormat:=wdFormatText, Encoding:=65001, _
        AddToRecentFiles:=False, AllowSubstitutions:=False, LineEnding:=wdCRLF
    
    
    '在Word中关闭TXT文档，打开DOCX文档
    ActiveDocument.Close 0
    Documents.Open filename:=DocxPath
    'ActiveDocument.Save
    
    
    '打开TXT文件
    Shell ("notepad " & TextPath)


End Sub


