from base_api import BaseCore

from functools import cached_property
from modules.consts import *

core = BaseCore()

def refresh_core():
    global core
    core = BaseCore()


class Video:
    def __init__(self, url):
        self.url = url
        self.content = core.fetch(self.url)

    @cached_property
    def title(self):
        return REGEX_TITLE.search(self.content).group(1)

    @cached_property
    def pornstars(self):
        matches = REGEX_AUTHOR.findall(self.content)
        actual_pornstars = []
        for match in matches:
            actual_pornstars.append(match[1])

        return actual_pornstars

    @cached_property
    def thumbnail(self):
        return REGEX_THUMBNAIL.search(self.content).group(1)

    @cached_property
    def m3u8_base_url(self) -> str:
        url =  REGEX_M3U8.search(self.content).group(0)
        fixed_url = url.replace("\\/", "/")  # Fixing escaped slashes
        return fixed_url

    def get_segments(self, quality):
        core.get_segments(self.m3u8_base_url, quality)

    def download(self, quality):
        core.download(video=self, quality=quality, downloader="threaded", path="./fortnite.mp4")

class Client:
    def get_video(self, url):
        return Video(url)
