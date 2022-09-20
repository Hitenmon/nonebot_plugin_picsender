## 前言
来自[anlen123](https://github.com/anlen123/nonebot_plugin_pixiv)的项目，精简了/.IDEA和Pypi，增加了一些功能。

这个插件我看到的时候就想到了telegram的发链接显示图的功能，很感兴趣，于是就拿来用了，还在添加功能。

### 计划
- 可以发送推特图片——未实装，正在研究怎么绕过AJAX
- 可以根据tag搜索并发送图片——已实装
- 可以根据用户发送图片 ——未实装

## 使用方法

在/src/plugins文件夹内直接git clone即可

### 指令


#### 发图

- pixiv pid：如pixiv 233233，会发送对应pid的图片
- 直接发送pixiv链接：如https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)，会自动识别

#### 排行榜

- pixivRank 天数：pixivRank 1 - 日榜，pixivRank 7 - 周榜，pixivRank 30 - 月榜

#### 图片搜索

- pixivTag tags：搜索并随机发送一张对应tag的图片，如：pixivTag ステンMK-II
- pixivTag5 tags：五连，搜索并随机发送五张对应tag的图片，如：pixivTag5 ステンMK-II

### 其他说明

指令大小写均可

排行榜和图片搜索功能会同时发送图片链接

关于图片搜索：
- 图片搜索的默认选项是添加 (1000 OR 2000 OR 5000) 的tag，即只从1000以上用户收藏中搜索，要搜索对应tag的全部图片，请添加all指令pixivTag all tags，如：pixivTag all ステンMK-II
- 此外，随机发图默认在第一页中随机，要查看搜索结果的其他页面，请添加pX指令pixivTag pX tags，如：pixivTag p2 ステンMK-II


### 配置
一共有四个配置项目

`IMGROOT=/root/`：保存图片的根目录

`AIOHTTP=http://127.0.0.1:1081`：http代理地址

`FFMPEG=/usr/bin/ffmpeg`：ffmpeg地址(不配置这个不支持动图)

`PIXIV_COOKIES=xxx`：你的p站的cookies (不配置不支持R18)

`PIXIV_R18=True`：是否支持R18 （默认支持）
