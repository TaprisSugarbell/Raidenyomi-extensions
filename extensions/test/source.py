import requests
import re
from bs4 import BeautifulSoup
import os
from main.models import chapter, download, extension
from main.Backend.IfOnline import connected
extensionId = extension.objects.get(name="Test").id
proxy = f"/bypass/{extensionId}/"


def SearchManga(query):
    """
    Searches Manhwaweb for a specifc manga
    """
    if connected():
        try:
            items = requests.get(
                f"https://manhwawebbackend-production.up.railway.app/manhwa/"
                f"library?buscar={query}&estado=&tipo=&erotico=&demografia=&order_item=alfabetico&order_dir=desc&page=0&generes="
            ).json()
            Results = {}
            for item in items["data"]:
                Name = item["the_real_name"]
                Results[Name] = [
                    f"https://manhwaweb.com/manhwa/{item["real_id"]}",
                    item["_imagen"],
                    False]
            return Results
        except Exception as e:
            print(e)
            return -1
    else:
        return


def GetMetadata(manga_url):
    """
    Gets all metadata for a certain manga
    """
    if connected():
        try:
            content = requests.get(
                f"https://manhwawebbackend-production.up.railway.app/manhwa/see/{manga_url.split('/')[-1]}").json()
            mangaInfo = {
                "name": content.get("the_real_name"),
                "url": manga_url,
                "cover": content.get("_imagen"),
                "author": "Unknown",
                "description": content.get("_sinopsis"),
            }
            return mangaInfo
        except Exception as e:
            print(e)
            return -1
    else:
        return -1


def GetChapters(manga_url):
    """
    Gets chapter info for a specific manga
    info includes name and upload date
    """
    if connected():
        try:
            content = requests.get(
                f"https://manhwawebbackend-production.up.railway.app/manhwa/see/{manga_url.split('/')[-1]}").json()
            Chapters = []
            for chap in content["chapters"][::-1]:
                ChapterName = f"Chapter {chap['chapter']}"
                ChapterLink = chap["link"]
                Chapters.append({"name": ChapterName, "url": ChapterLink})
            return Chapters
        except Exception as e:
            print(e)
            return -1
    else:
        return -1


def GetImageLinks(page_url):
    """
    scrapes links for all images of a specific chapter
    """
    if connected():
        try:
            chapter = requests.get(
                f"https://manhwawebbackend-production.up.railway.app/chapters/see/{page_url.split('/')[-1]}"
            ).json()
            urls = [proxy+image for image in chapter["chapter"]["img"]]
            return urls
        except Exception as e:
            print(e)
            return []
    else:
        return []

def GetImageLinksNoProxy(page_url):
    """
    scrapes links for all images of a specific chapter
    """
    if connected():
        try:
            chapter = requests.get(
                f"https://manhwawebbackend-production.up.railway.app/chapters/see/{page_url.split('/')[-1]}"
            ).json()
            urls = [image for image in chapter["chapter"]["img"]]
            return urls
        except Exception as e:
            print(e)
            return []
    return []

def DownloadChapter(urls, comicid, chapterId, downloadId):
    """
    Takes in url for a manga page and downloads it
    for now the images are going to be downloaded in the working directory"""
    headers = {
        'Referer': "https://manhwaweb.com/",
    }
    path = fr"{os.getcwd()}\main\static\manga\{comicid}\{chapterId}"
    if not os.path.exists(path):
        os.makedirs(path)

    for index,url in enumerate(urls):
        try:
            response = requests.get(url, headers=headers)
            file_name = fr"{path}\{index+1}.{url[len(url)-3::]}"
            print(file_name)
            if not download.objects.all().filter(id=downloadId).exists():
                break
            chapterToDownload = download.objects.get(id=downloadId)
            with open(file_name, "wb") as image:
                image.write(response.content)

            chapterToDownload.downloaded += 1
            chapterToDownload.save()
        except Exception as e:
            print(e)
            download.objects.get(id=downloadId).delete()
            return True

    if not download.objects.all().filter(id=downloadId).exists():
        return False