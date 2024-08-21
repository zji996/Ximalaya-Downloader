import main
import asyncio
import re
import requests
import os
import json
from fake_useragent import UserAgent
import tkinter as tk
from tkinter import filedialog

current_version = main.version
ximalaya = main.Ximalaya()
ua = UserAgent()

def select_directory():
    root = tk.Tk()
    root.withdraw()
    directory_path = filedialog.askdirectory()
    root.destroy()
    return directory_path

def get_latest_release():
    url = "https://api.github.com/repos/Diaoxiaozhang/Ximalaya-Downloader/releases/latest"
    response = requests.get(url)
    version = response.json()["tag_name"]
    release_url = response.json()["html_url"]
    return version, release_url

async def download_sound(sound_id, headers, path):
    sound_info = ximalaya.analyze_sound(sound_id, headers)
    if sound_info is False:
        return
    if sound_info == 0:
        print(f"ID为{sound_id}的声音解析为vip声音或付费声音，但当前登录账号未购买！")
        return
    print(f"成功解析声音{sound_info['name']}，下载普通音质")
    ximalaya.get_sound(sound_info["name"], sound_info[1], path)

async def download_album(album_id, headers, path):
    album_name, sounds = ximalaya.analyze_album(album_id)
    if not sounds:
        return
    album_type = ximalaya.judge_album(album_id, headers)
    if album_type == 0 or album_type == 1:
        start = 1
        end = len(sounds)
        number = True  # 假设需要在文件名中加入序号
        quality_choice = 2  # 假设选择普通音质
        await ximalaya.get_selected_sounds(sounds, album_name, start, end, headers, quality_choice, number, path)
    elif album_type == 2:
        print(f"专辑 {album_id} 是付费专辑，当前未购买或未开通vip")
    else:
        print(f"专辑 {album_id} 解析失败")

async def main():
    print("欢迎使用喜马拉雅下载器")
    latest_version, latest_release_url = get_latest_release()
    if latest_version == current_version:
        print("当前您使用的已是最新版本，如果遇到任何问题，请前往github提交issue")
    else:
        print("您当前使用的并非最新版本，强烈建议前往github下载最新版本")
        print(f"下载链接：{latest_release_url}")
    
    cookie, path = ximalaya.analyze_config()
    if not cookie:
        print("未检测到有效喜马拉雅登录信息，请登录后再使用")
        ximalaya.login()
        headers = {
            "user-agent": ua.random,
            "cookie": ximalaya.analyze_config()[0]
        }
    else:
        username = ximalaya.judge_cookie(cookie)
        if username:
            print(f"已检测到有效登录信息，当前登录用户为{username}，如需切换账号请删除config.json文件然后重新启动本程序！")
            headers = {
                "user-agent": ua.random,
                "cookie": ximalaya.analyze_config()[0]
            }
        else:
            print("未检测到有效喜马拉雅登录信息，请登录后再使用")
            ximalaya.login()
            headers = {
                "user-agent": ua.random,
                "cookie": ximalaya.analyze_config()[0]
            }
    
    if not os.path.isdir(path):
        print('在config文件中未检测到有效的下载路径，将使用默认下载路径./download')
        path = './download'
    
    with open("album_list.txt", "r") as file:
        urls = file.readlines()
    
    tasks = []
    for url in urls:
        url = url.strip()
        if "sound" in url:
            try:
                sound_id = re.search(r"sound/(?P<sound_id>\d+)", url).group('sound_id')
                tasks.append(download_sound(sound_id, headers, path))
            except Exception:
                print(f"解析声音链接 {url} 失败")
        elif "album" in url:
            try:
                album_id = re.search(r"album/(?P<album_id>\d+)", url).group('album_id')
                tasks.append(download_album(album_id, headers, path))
            except Exception:
                print(f"解析专辑链接 {url} 失败")
        else:
            print(f"无效的链接 {url}")

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())