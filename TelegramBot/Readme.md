## Telegram Bot 目录

### 部分脚本为bot调用做了优化  
请使用 **本目录** （而非主目录）下的脚本
~~反向替代应该没什么问题~~
```
Novels.py
PrintTags.py
FileOperate.py
```


### 依赖：

```
## 必需
pip install pixivpy
pip install python-telegram-bot
pip install python-docx
pip install opencc-python-reimplemented
## 或使用官方的OpenCC
pip install opencc

## 非必需
## 你的bot不会跑在Windows上吧？
pip install pywin32
```