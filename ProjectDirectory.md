## 项目结构

### 小说推荐
```
📂 小说推荐      #存放小说文件 docx，不公开分享  
├── 📂 2021     #按照年月分类
│    └── 📂 04
├── 📂 2022
│    └── 📂 01
├── 📂 工具
│    ├── 📜 ConvertAll.py   #docx转txt，并进行繁简转换
│    ├── 📜 GetTags.py      #根据文件内的标签转换标签
│    └── 📜 Tags.md         #由 GetTags.py 生成
└── 📜 繁简转换说明.docx
```
### 兽人小说

```
📂 兽人小说      #存放小说，并公开分享
├── 📂小说推荐   #存放小说文件 txt，由 ConvertAll.py 生成
│    ├── 📂 频道版   #无繁简转换
│    ├── 📂 简体版   #转换成简体
│    └── 📂 繁體版   #转换成繁体
├── 📂小说合集 
│    ├── 📂 本频道
│    │    └──📜 2021合集.zip
│    └── 📂 其他分享
└── 📜 说明.txt    #UTF8 GBK BIG5 三种编码各一份
```

### 二者关系

```
📂某目录 
├── 📂 小说推荐
│    └──📂 工具
├── 📂 兽人小说
│    └──📂 小说推荐 
└── 📜 其他文件
```

## 使用说明

装好第三方库，并在对应目录放置好文件后，或者你修改好对应目录后，就应该可以用了
```python
pip install python-docx
pip install pywin32
pip install pixivpy
pip install opencc-python-reimplemented
或使用官方的OpenCC
pip install opencc
```

### 涉及到Word文档的内容
需要开启 **正文缩进 / Normal Indent** 样式，具体方式请自行百度  
可以使用 **小说.dotm**作为模板（模板中已开启此样式）  
需要开启**开发工具**选项卡，并在**宏安全性**中启用宏  
启用之后，即可使用VBA代码，自动按照相应进行排版
### 配合 FileOperate.py 内的 saveDocx 可以做到写入文件后全自动排版

如果你安装了` python-docx `模块也可以这样（见 Normal_Indent.py）开启正文缩进  
就算你启用了正文缩进，也无法在python docx 里直接使用此样式  
不如直接用设定好样式的模板
