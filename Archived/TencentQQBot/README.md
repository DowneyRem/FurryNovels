## @FurryNovelsBot On Tencent QQ

https://github.com/DowneyRem/FurryNovels/tree/main/TencentQQBot

### 使用方法

（类似吧）https://telegra.ph/FurryNovelsReading-04-04-07

### 主要功能

1. 下载功能：
   - 下载单篇小说，打包下载系列小说，打包下载作者合集
   - 下载后，自动翻译外语小说
2. 翻译功能：
   - 使用 OpenCC ，进行繁简转换
   - 使用谷歌翻译，翻译外语小说
3. 投稿功能：
   - 从下载的小说中，根据标签和正文筛选出兽人小说
   - 从筛选后的兽人小说中，选取其中的高质量小说
   - 发送到 @FurryReading 和 @FurryNovels 两个频道中

### 项目结构
#### /TencentQQbot 主目录：
| 文件名          | 功能                       |
| :-------------- | :------------------------- |
| bot.py          | nonebot 主程序 |
| config.py       | nonebot 配置文件 |
| QQbot.bat       | 启动GOCPHTTP，启动 bot.py |

#### /plguins 目录：
几个简单的小插件
| 文件(夹)名        | 功能                       |
| :--------------  | :------------------------- |
| NovelsDownloader | 下载小说；翻译小说         |
| NovelsTranslator | 翻译小说的帮助             |
| usuage.py        | 帮助功能                   |
| notice.py        | 消息群发                   |
| request.py | 通过好友验证，接受入群邀请 |

#### /plguins/NovelsDownloader 目录：
除了加粗部分，其他都一样
| 文件名           | 功能                       |
| :-------------- | :------------------------- |
| FileOperate     | 文件读写、压缩、解压       |
| GetLanguage     | 获取文本语言               |
| MakeTags        | 生成标签、读取标签         |
| PixivClass      | 批量下载 Pixiv 小说        |
| PrintInfo       | 通过匹配文字获取小说标签     |
| Recommend       | Pixiv网页 api 获取推荐小说 |
| **TelegramBot** | **上传 Telegram 频道**  |
| **TencetQQBot** | **QQBot 功能**         |
| **`__init__`**  | **QQBot 调用入口** |
| TextFormat      | 文本重新排版               |
| TokenRoundRobin | Pixiv token 轮转请求       |
| Translate       | 翻译标签，翻译文档         |
| configuration   | 配置文件                   |

####  /plguins/NovelsDownloader/data 目录：
这里完全一样。但是为了避免你再翻一次，就直接抄过来了
| 文件名            | 功能                         |
| ---------------- | ---------------------------- |
| hashtag.json     | 【供龙类编辑的】小说标签     |
| races.json       | 【供龙类编辑的】种族标签     |
| usedtags.json    | 【供程序使用的】标签         |
| translated.json  | 【供龙类编辑的】常用翻译词组 |
| translation.json | 【供程序使用的】常用翻译词组 |
| 模板              | word 文档模板                |


### 不予公开的内容
1. Pixiv 的 refresh token
2. Telegram Bot 的 token
3. Webdav 的 token
4. QQ 号码，QQ 的 token

### 部署指南
1. 下载 GoCQhttp 
2. 克隆 QQbot 代码
3. 装好第三方库，
4. 双击运行` QQbot.bat ` 

**Python 310 下可用**【2022-11-22】

**保证两个监听的IP和端口一致就可以了**
#### Nonebot 部分配置

```
# WS默认监听的 IP 和端口
HOST = '127.0.0.1'
PORT = 8080
```

#### GoCQhttp 部分配置

```
# 连接服务列表
servers:
  # 添加方式，同一连接方式可添加多个，具体配置说明请查看文档
  #- http: # http 通信
  #- ws:   # 正向 Websocket
  #- ws-reverse: # 反向 Websocket
  #- pprof: #性能分析服务器
  # 反向WS设置
  - ws-reverse:
      # 反向WS Universal 地址
      # 注意 设置了此项地址后下面两项将会被忽略
      universal: ws://127.0.0.1:8080/ws/
      # 反向WS API 地址
      api:  ws://127.0.0.1:8080/ws/api
      # 反向WS Event 地址
      event: ws://127.0.0.1:8080/ws/event/
      # 重连间隔 单位毫秒
      reconnect-interval: 3000
      middlewares:
        <<: *default # 引用默认中间件
```
