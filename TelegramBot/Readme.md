## Telegram Bot 公开版

请根据不同平台调整并部署

依赖详见 Requirement.txt

### 与非公开版的区别

- Bot 的 Token

- Pixivpy 的  Refresh Token

- 其他运行 bot 所需要的服务

### 与 Local Version 目录的区别

- 使用场景不同
  - TelegramBot 目录下为bot使用的版本
  - Python 目录下文件为个龙使用的版本（已停用）

- 少数文件不同
  - Convert.py 与 ConertAll.py (转换逻辑不同)
  - TelegramBot.py (废话)
  - Webdav3 与 Webdav4
  
  

## 主页功能与使用方法

###  主要功能

1. (优雅地)下载Pixiv小说
1. 同时向频道投稿

### 使用方法

向 Bot 发送Pixiv小说链接即可下载小说，并同时向频道分享

## 缺陷与进一步的功能优化

### 目前的缺陷
0. 没有人类或兽人使用
1. Pixiv 的请求限制（只要不疯狂请求，应该够用）
1. 下载过的小说会重复下载
1. Heroku 服务器的时间限制（目前够用）
1. 单线程下载耗时较长（比复制粘贴快）
1. 未处理多用户同时使用的情况

### 有待优化的功能

- ~~获取并更换 Refresh Token~~（目前还不会）
- 文件下载与管理
- 根据正文获取小说标签
- ~~多线程下载~~（目前还不会）
- ~~多用户功能优化~~（目前还不会）

