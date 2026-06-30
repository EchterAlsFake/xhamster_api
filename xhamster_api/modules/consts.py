import re

from typing import List
from selectolax.lexbor import LexborHTMLParser

REGEX_M3U8 = re.compile(r'https://[^"]*?_TPL_\.(?:h264|av1)\.mp4\.m3u8')
REGEX_AUTHOR = re.compile(r'<div class="item-[^"]*?">.*?<img[^>]+?alt="([^"]+?)"[^>]*?>.*?<span class="body-[^"]*? label-[^"]*? label-[^"]*?">([^<]+?)</span>')
REGEX_AUTHOR_SHORTS = re.compile(r'"name":"(.*?)"')
REGEX_THUMBNAIL = re.compile(r'<meta property="og:image" content="(.*?)"/>')
REGEX_LENGTH = re.compile(r'<span class="eta">(.*?)</span>')
REGEX_AVATAR = re.compile(r"background-image: url\('(.*?)'\)")


REGEX_LIKES_SHORTS = re.compile(r'"likes":(.*?),"')

headers = {
    "Referer": "https://www.xhamster.com/"
}


def extractor_shorts(content: str) -> List[str]:
    soup = LexborHTMLParser(content)
    nodes = soup.css("a.imageContainer-a870e.role-pop.thumb-image-container.thumb-image-container--moment")
    stuff = [n.attributes.get("href") for n in nodes if n and n.attributes.get("href")]
    return stuff

def build_page_url(url: str, is_search: bool, idx: int) -> str:
    if is_search:
        # query-string pagination
        joiner = "&" if "?" in url else "?"
        return f"{url}{joiner}page={idx}"

    if idx == 1:
        return url

    return f"{url}/{idx}"

