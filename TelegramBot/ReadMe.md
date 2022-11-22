## @FurryNovelsBot
https://github.com/DowneyRem/FurryNovels/tree/main/TelegramBot

### 使用方法
https://telegra.ph/FurryNovelsReading-04-04-07

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
#### 主目录：
| 文件名          | 功能                       |
| :-------------- | :------------------------- |
| FileOperate     | 文件读写、压缩、解压       |
| GetLanguage     | 获取文本语言               |
| MakeTags        | 生成标签、读取标签         |
| PixivClass      | 批量下载 Pixiv 小说        |
| Recommend       | Pixiv网页 api 获取推荐小说 |
| TelegramBot     | TelegramBot 调用入口       |
| TextFormat      | 文本重新排版               |
| TokenRoundRobin | Pixiv token 轮转请求       |
| Translate       | 翻译标签，翻译文档         |
| configuration   | 配置文件                   |

#### data 目录：
| 文件名           | 功能                         |
| ---------------- | ---------------------------- |
| hashtag.json     | 【供龙类编辑的】小说标签     |
| races.json       | 【供龙类编辑的】种族标签     |
| usedtags.json    | 【供程序使用的】标签         |
| translated.json  | 【供龙类编辑的】常用翻译词组 |
| translation.json | 【供程序使用的】常用翻译词组 |
| 模板             | word 文档模板                |


### 不予公开的内容
1. Pixiv 的 refresh token
1. Telegram Bot 的 token
3. Webdav 的 token

### 部署指南
**我自己都是找别人帮我部署的，你还是自求多福吧**

~~其实装好第三方库，双击运行还是挺简单的~~

**Python 310 下可用 【2022-11-22】**

