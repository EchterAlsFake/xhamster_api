import re

from bs4 import BeautifulSoup
from typing import List
REGEX_M3U8 = re.compile(r'https://[^"]*?_TPL_\.(?:h264|av1)\.mp4\.m3u8')
REGEX_TITLE = re.compile(r'<meta property="og:title" content="(.*?)"')
REGEX_AUTHOR = re.compile(r'<div class="item-[^"]*?">.*?<img[^>]+?alt="([^"]+?)"[^>]*?>.*?<span class="body-[^"]*? label-[^"]*? label-[^"]*?">([^<]+?)</span>')
REGEX_AUTHOR_SHORTS = re.compile(r'body-bold-8643e label-5984a label-96c3e">(.*?)</span>')
REGEX_THUMBNAIL = re.compile(r'<meta property="og:image" content="(.*?)">')
REGEX_LENGTH = re.compile(r'<span class="eta">(.*?)</span>')
REGEX_AVATAR = re.compile(r"background-image: url\('(.*?)'\)")


REGEX_LIKES_SHORTS = re.compile(r'"likes":(.*?),"')

headers = {
    "Referer": "https://www.xhamster.com/"
}

def extractor_html(content: str) -> List[str]:
    soup = BeautifulSoup(content, "lxml")
    nodes = soup.find_all("a",class_="video-thumb__image-container role-pop thumb-image-container")
    return [n.get("href") for n in nodes if n and n.get("href")]


def extractor_shorts(content: str) -> List[str]:
    soup = BeautifulSoup(content, "lxml")
    nodes = soup.find_all("a", class_="imageContainer-a870e role-pop thumb-image-container thumb-image-container--moment")
    return [n.get("href") for n in nodes if n and n.get("href")]

def build_page_url(url: str, is_search: bool, idx: int) -> str:
    if is_search:
        # query-string pagination
        joiner = "&" if "?" in url else "?"
        return f"{url}{joiner}page={idx}"

    if idx == 1:
        return url

    return f"{url}/{idx}"

