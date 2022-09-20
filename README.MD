## 前言
来自[anlen123](https://github.com/anlen123/nonebot_plugin_pixiv)的项目，精简了/.IDEA和Pypi，增加了一些功能。

这个插件我看到的时候就想到了telegram的发链接显示图的功能，很感兴趣。

### 计划
- 可以发送推特图片——未实装，正在研究怎么绕过AJAX

- 可以根据tag搜索并发送图片——已实装

- 可以根据用户发送图片 ——未实装

## 使用方法

在/src/plugins文件夹内直接git clone即可

### 指令

pixiv pid

pixivRank 数字

pixivTag tags

pixivTag5 tags

大小写均可，例如：

pixiv 233

pixiv 1000

pixivRank 1 - 日榜

pixivRank 7 - 周榜

pixivRank 30 - 月榜

pixivTag ステンMK-II - 随机获取1张热门的司登的图

pixivTag5 ステンMK-II - 随机获取5张热门的司登的图

周榜和Tag检索都会发送图片链接

直接发这种链接也能直接识别发送图片

https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)

### 配置
一共有四个配置项目

IMGROOT=/root/

AIOHTTP=http://127.0.0.1:1081

FFMPEG=/usr/bin/ffmpeg

PIXIV_COOKIES=xxx

PIXIV_R18=True

分别是:

1.保存图片的根目录

2.http代理地址

3.ffmpeg地址(不配置这个不支持动图)

4.你的p站的cookies (不配置不支持R18)

5.是否支持R18 （默认支持）

