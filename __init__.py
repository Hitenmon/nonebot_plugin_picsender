from asyncio import events
from urllib import response
from weakref import proxy
import nonebot
from pathlib import Path
from typing import List
from nonebot import run
from nonebot.rule import Rule
from nonebot.plugin import on_message, on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment, GroupMessageEvent
import aiohttp
import re
import os
import random
import cv2
import asyncio
import base64
import json

_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "plugins").
        resolve()))

global_config = nonebot.get_driver().config
config = global_config.dict()

# 读取Config
imgRoot = config.get('imgroot') if config.get(
    'imgroot') else f"{os.environ['HOME']}/"
proxy_aiohttp = config.get('aiohttp') if config.get('aiohttp') else ""
pixiv_cookies = config.get('pixiv_cookies') if config.get(
    'pixiv_cookies') else ""
twitter_cookies = config.get('twitter_cookies') if config.get(
    'twitter_cookies') else ""
ffmpeg = config.get('ffmpeg') if config.get('ffmpeg') else "/usr/bin/ffmpeg"
pixiv_r18 = config.get('pixiv_r18') if config.get('pixiv_r18') else "True"
pixiv_r18 = eval(pixiv_r18)

pathHome = imgRoot + "QQbotFiles/pixiv"
if not os.path.exists(pathHome):
    os.makedirs(pathHome)

pathZipHome = imgRoot + "QQbotFiles/pixivZip"
if not os.path.exists(pathZipHome):
    os.makedirs(pathZipHome)

headersCook = {
    'referer': 'https://www.pixiv.net',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}

twiHeadersCook = {
    'referer': 'https://twitter.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
}

if pixiv_cookies:
    headersCook['cookie'] = pixiv_cookies
if twitter_cookies:
    headersCook['cookie'] = twitter_cookies


async def checkConfig(bot: Bot, event: Event) -> bool:
    if not pixiv_cookies:
        await bot.send(event=event, message="pixiv_cookies未配置!!")
        return False
    return True


def isPixivURL() -> Rule:
    async def isPixivURL_(bot: "Bot", event: "Event") -> bool:
        if event.get_type() != "message":
            return False
        msg = str(event.get_message())
        if re.findall("https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)", msg):
            return True
        return False

    return Rule(isPixivURL_)


def isTwitterURL() -> Rule:
    async def isTwitterURL_(bot: "Bot", event: "Event") -> bool:
        if event.get_type() != "message":
            return False
        msg = str(event.get_message())
        if re.findall("https://twitter.com/\w+/status/\d+", msg):
            return True
        return False

    return Rule(isTwitterURL_)


pixivURL = on_message(rule=isPixivURL())


@pixivURL.handle()
async def pixivURL(bot: Bot, event: Event):
    if not await checkConfig(bot, event):
        return
    pid = re.findall(
        "https://www.pixiv.net/artworks/(\d+)|illust_id=(\d+)", str(event.get_message()))
    if pid:
        pid = [x for x in pid[0] if x][0]
        isGIF = (await checkGIF(pid))
        if isGIF != "NO":
            await GIF_send(isGIF, pid, event, bot)
        else:
            await send(pid, event, bot)


# twitterURL = on_message(rule=isTwitterURL())


# @twitterURL.handle()
# async def twitterURL_handle(bot: Bot, event: Event):
#     if not await checkConfig(bot, event):
#         return
#     url = re.findall("https://twitter.com/\w+/status/\d+",
#                      str(event.get_message()))
#     if url:
#         await bot.send(event=event, message='虽然我没办法帮你发推特里的图，但是还是可以复读一下链接来安慰你的'+url[0])
        # names = await twiFetch(url, event, bot)
        # await twiSend(names, event, bot)


# async def twiFetch(url: str, event: Event, bot: Bot):
#     print("发送请求：", url)
#     names = []
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url=url, headers=twiHeadersCook, proxy=proxy_aiohttp) as page:
#             content = await page.content.read()
#             down_url = re.findall(
#                 '"original":"(.*?)\.(png|jpg|jepg)"', content.decode())
#             if not down_url:
#                 return names
#             url = '.'.join(down_url[0])
#             name = url[url.rfind("/") + 1:]
#             num = 1
#             names = []
#     async with session.get(url=url, headers=twiHeadersCook, proxy=proxy_aiohttp) as response:
#         # async with session.get(url=url, headers=headers) as response:
#         code = response.status
#         if code == 200:
#             content = await response.content.read()
#             with open(f"{imgRoot}QQbotFiles/pixiv/" + name, mode='wb') as f:
#                 f.write(content)
#     return names


# async def twiSend(names, event: Event, bot: Bot):
#     return

pixiv = on_regex(pattern="^pixiv\ ")


@pixiv.handle()
async def pixiv_rev(bot: Bot, event: Event):
    if not await checkConfig(bot, event):
        return
    pid = str(event.message).strip()[6:].strip()
    if (not pixiv_r18) and await isR18(pid):
        await bot.send(event=event, message="不支持R18，请修改配置后操作！")
        return
    isGIF = (await checkGIF(pid))
    if isGIF != "NO":
        await GIF_send(isGIF, pid, event, bot)
    else:
        await send(pid, event, bot)


async def fetch(session, url, name):
    print("发送请求：", url)
    async with session.get(url=url, headers=headersCook, proxy=proxy_aiohttp) as response:
        # async with session.get(url=url, headers=headers) as response:
        code = response.status
        if code == 200:
            content = await response.content.read()
            with open(f"{imgRoot}QQbotFiles/pixiv/" + name, mode='wb') as f:
                f.write(content)
            return True
        return False


async def main(PID):
    url = f"https://www.pixiv.net/artworks/{PID}"
    async with aiohttp.ClientSession() as session:
        page = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        # page = await session.get(url=url, headers=headers)
        content = await page.content.read()
        down_url = re.findall(
            '"original":"(.*?)\.(png|jpg|jepg)"', content.decode())
        if not down_url:
            return ""
        url = '.'.join(down_url[0])
        name = url[url.rfind("/") + 1:]
        num = 1
        names = []
        if os.path.exists(f"{imgRoot}QQbotFiles/pixiv/" + name):
            hou = down_url[0][1]
            while os.path.exists(f"{imgRoot}QQbotFiles/pixiv/" + name) and num <= 6:
                names.append(name)
                newstr = f"_p{num}.{hou}"
                num += 1
                name = re.sub("_p(\d+)\.(png|jpg|jepg)", newstr, name)
        else:
            hou = down_url[0][1]
            while (await fetch(session=session, url=url, name=name) and num <= 6):
                names.append(name)
                newstr = f"_p{num}.{hou}"
                num += 1
                url = re.sub("_p(\d+)\.(png|jpg|jepg)", newstr, url)
                name = url[url.rfind("/") + 1:]
        return names


async def getImgsByDay(days):
    async with aiohttp.ClientSession() as session:
        if days == 'day':
            url = 'https://www.pixiv.net/ranking.php'
        else:
            url = f'https://www.pixiv.net/ranking.php?mode={days}'
        # response = await session.get(url=url,headers=headers)
        response = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        text = (await response.content.read()).decode()
        imgs = set(re.findall('\<a href\=\"\/artworks\/(.*?)\"', text))
        return list(imgs)

pixivRank = on_regex(pattern="^pixivRank\ ")

@pixivRank.handle()
async def pixiv_rev(bot: Bot, event: Event):
    if not await checkConfig(bot, event):
        return
    info = str(event.message).strip()[10:].strip()
    dic = {
        "1": "day",
        "7": "weekly",
        "30": "monthly"
    }
    if info in dic.keys():
        imgs = random.choices(await getImgsByDay(dic[info]), k=5)
        await send_group_imgs(bot, event, imgs)
    else:
        await bot.send(event=event, message=Message("参数错误\n样例: 'pixivRank 1' , 1:day,7:weekly,30:monthly"))

async def send_group_imgs(bot: Bot, event: Event, imgs):
    names = []
    for img in imgs:
        names.append(await main(img))
    if not names:
        await bot.send(event=event, message="发生了异常情况")
    else:
        msg = None
        for name in names:
            if name:
                for t in name:
                    path = f"{imgRoot}QQbotFiles/pixiv/{t}"
                    size = os.path.getsize(path)
                    if size // 1024 // 1024 >= 10:
                        await yasuo(path)
                    msg += MessageSegment.image(await base64_path(path))
        try:
            if isinstance(event, GroupMessageEvent):
                await send_forward_msg_group(bot, event, 'qqbot', msg)
            else:
                await bot.send(event=event, message=msg)
        except:
            await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查")


pixivTag= on_regex(pattern="^(?i)[pixivTag|pixivtag5]")

@pixivTag.handle()
async def pixiv_tag_handler(bot : Bot, event: Event):
    msg_plain_text = str(event.message).split(' ', 2)
    if msg_plain_text[1] == 'all':
        manyUsers = ''
        msg_plain_text.pop(1)
    else:
        manyUsers = ' 1000'
    tag_plain_text = msg_plain_text[1]
    print(msg_plain_text[0], manyUsers, tag_plain_text)
    url = "https://www.pixiv.net/ajax/search/artworks/"+tag_plain_text+manyUsers+'?word='+tag_plain_text+manyUsers
    if pixiv_r18:
        url = url + '&order=date_d&p=1&s_mode=s_tag&type=all&lang=zh'
    else:
        url = url + '&order=date_d&mode=safe&p=1&s_mode=s_tag&type=all&lang=zh'
    img_set = await getImgByTag(url)
    if img_set:
        if msg_plain_text[0] in ["pixivTag", "pixivtag"]:
            imgs = random.choices(img_set, k=1)
        elif msg_plain_text[0] in ["pixivTag5", "pixivtag5"]:
            imgs = random.choices(img_set, k=5)
        await send_group_imgs(bot, event, imgs)
    else:
        await pixivTag.finish("没有搜到作品哦")


async def getImgByTag(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headersCook, proxy=proxy_aiohttp) as resp:
            content = await resp.content.read()
            imgs = set(re.findall('"id":"([0-9]+)",', content.decode()))
            return list(imgs)
    

async def base64_path(path: str):
    ff = "空"
    with open(path, "rb") as f:
        ff = base64.b64encode(f.read()).decode()
    return f"base64://{ff}"


async def send(pid: str, event: Event, bot: Bot):
    names = await main(pid)
    if not names:
        await bot.send(event=event, message="没有这个pid的图片")
    else:
        msg = None
        for name in names:
            path = f"{imgRoot}QQbotFiles/pixiv/{name}"
            size = os.path.getsize(path)
            if size // 1024 // 1024 >= 10:
                await yasuo(path)
            msg += MessageSegment.image(await base64_path(path))
        try:
            if isinstance(event, GroupMessageEvent):
                await send_forward_msg_group(bot, event, 'qqbot', msg)
            else:
                await bot.send(event=event, message=msg)

        except:
            await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查,尝试一张一张的发图片ing")
            try:
                for name in names:
                    path = f"{imgRoot}QQbotFiles/pixiv/{name}"
                    size = os.path.getsize(path)
                    if size // 1024 // 1024 >= 10:
                        await yasuo(path)
                    await bot.send(event=event, message=MessageSegment.image(await base64_path(path)))
            except:
                await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查!!!")


async def yasuo(path):
    while os.path.getsize(path) // 1024 // 1024 >= 10:
        image = cv2.imread(path)
        shape = image.shape
        res = cv2.resize(
            image, (shape[1] // 2, shape[0] // 2), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f"{path}", res)


async def checkGIF(pid: str) -> str:
    url = f'https://www.pixiv.net/ajax/illust/{pid}/ugoira_meta'
    async with aiohttp.ClientSession() as session:
        x = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        content = await x.json()
        if content['error']:
            return "NO"
        return content['body']['originalSrc']


async def GIF_send(url: str, pid: str, event: Event, bot: Bot):
    path_pre = f"{imgRoot}QQbotFiles/pixivZip/{pid}"
    if os.path.exists(f"{path_pre}/{pid}.gif"):
        size = os.path.getsize(f"{path_pre}/{pid}.gif")
        while size // 1024 // 1024 >= 15:
            msg = await run(f"file {path_pre}/{pid}.gif")
            cheng = int(msg.split(" ")[-3]) // 2
            kuan = int(msg.split(" ")[-1]) // 2
            await run(f"{ffmpeg} -i {path_pre}/{pid}.gif -s {cheng}x{kuan} {path_pre}/{pid}_temp.gif")
            await run(f"rm -rf {path_pre}/{pid}.gif")
            await run(f"mv {path_pre}/{pid}_temp.gif {path_pre}/{pid}.gif")
            size = os.path.getsize(f"{path_pre}/{pid}.gif")
        try:
            await bot.send(event=event, message=MessageSegment.image(await base64_path(f"{path_pre}/{pid}.gif")))
        except:
            await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查")
        return
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        code = response.status
        if code == 200:
            content = await response.content.read()
            if not os.path.exists(f"{path_pre}.zip"):
                with open(f"{path_pre}.zip", mode='wb') as f:
                    f.write(content)
                if not os.path.exists(f"{path_pre}"):
                    os.mkdir(f"{path_pre}")
            await run(f"unzip -n {path_pre}.zip -d {path_pre}")
            image_list = sorted(os.listdir(f"{path_pre}"))
            await run(f"rm -rf {path_pre}.zip")
            await run(f"{ffmpeg} -r {len(image_list)} -i {path_pre}/%06d.jpg {path_pre}/{pid}.gif -n")
            # 压缩
            size = os.path.getsize(f"{path_pre}/{pid}.gif")
            while size // 1024 // 1024 >= 15:
                msg = await run(f"file {path_pre}/{pid}.gif")
                cheng = int(msg.split(" ")[-3]) // 2
                kuan = int(msg.split(" ")[-1]) // 2
                await run(f"{ffmpeg} -i {path_pre}/{pid}.gif -s {cheng}x{kuan} {path_pre}/{pid}_temp.gif")
                await run(f"rm -rf {path_pre}/{pid}.gif")
                await run(f"mv {path_pre}/{pid}_temp.gif {path_pre}/{pid}.gif")
                size = os.path.getsize(f"{path_pre}/{pid}.gif")
            try:
                await bot.send(event=event, message=MessageSegment.image(await base64_path(f"{path_pre}/{pid}.gif")))
            except:
                await bot.send(event=event, message="查询失败, 帐号有可能发生风控，请检查")


async def run(cmd: str):
    print(cmd)
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    return (stdout + stderr).decode()


# 合并消息
async def send_forward_msg_group(
        bot: Bot,
        event: GroupMessageEvent,
        name: str,
        msgs: List[str],
):
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": bot.self_id, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )


async def isR18(PID):
    print("判断是不是R18")
    url = f"https://www.pixiv.net/artworks/{PID}"
    async with aiohttp.ClientSession() as session:
        x = await session.get(url=url, headers=headersCook, proxy=proxy_aiohttp)
        content = await x.content.read()
        tags = re.findall('\"tags\"\:\[(.*?)\]', content.decode())[0]
        print(tags)
        if 'R-18' in tags:
            return True
        else:
            return False

# pixivS = on_regex(pattern="^来点")


# @pixivS.handle()
# async def pixivS_rev(bot: Bot, event: Event):
    # if not await checkConfig(bot, event):
        # return
    # pid = ""
    # key = str(event.message).strip()[2:].strip() + " 100users入り"
    # async with aiohttp.ClientSession() as session:
        # x = await session.get(url="https://www.pixiv.net/ajax/search/artworks/"+str(key), headers=headersCook, proxy=proxy_aiohttp)
        # # x = await session.get(url=url, headers=headers)
        # content = await x.content.read()
        # content = json.loads(content)
        # print(content['error'])
        # if not content['error']:
            # if content['body']['illustManga']['data']:
            # pid = random.choice(content['body']['illustManga']['data'])['id']
    # if pid:
        # xx = (await checkGIF(pid))
        # if xx != "NO":
            # await GIF_send(xx, pid, event, bot)
        # else:
            # await send(pid, event, bot)
    # else:
        # await bot.send(event=event,message="抱歉！没有搜索到任何内容")
