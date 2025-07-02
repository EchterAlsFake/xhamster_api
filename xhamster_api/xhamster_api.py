import os

from base_api import BaseCore
from functools import cached_property
from base_api.base import setup_logger

try:
    from modules.consts import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *


class Video:
    def __init__(self, url, core):
        self.core = core
        self.url = url
        self.logger = setup_logger(name="XHamster API - [Video]")
        self.content = self.core.fetch(self.url)

    def enable_logging(self, log_file: str = None, level=None):
        self.logger = setup_logger(name="XHamster API - [Video]", level=level, log_file=log_file)

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
        self.logger.debug(f"M3U8 URL: {fixed_url}")
        return fixed_url

    def get_segments(self, quality):
        return self.core.get_segments(self.m3u8_base_url, quality)

    def download(self, quality, downloader, path="./", no_title = False, callback=None):
        if no_title is False:
            path = os.path.join(path, self.title + ".mp4")


        self.core.download(video=self, quality=quality, downloader=downloader, path=path, callback=callback)

class Client:
    def __init__(self, core=None):
        self.core = core or BaseCore()

    def get_video(self, url):
        return Video(url, core=self.core)
