import os

from base_api import BaseCore
from functools import cached_property
from base_api.base import setup_logger

try:
    from modules.consts import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *

core = BaseCore()

def refresh_core(enable_logging=False, log_file: str = None, level=None):
    global core
    core = BaseCore()
    if enable_logging:
        core.enable_logging(log_file=log_file, level=level)


class Video:
    def __init__(self, url):
        self.url = url
        self.logger = setup_logger(name="XHamster API - [Video]")
        self.content = core.fetch(self.url)

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
        return core.get_segments(self.m3u8_base_url, quality)

    def download(self, quality, downloader, path="./", no_title = False, callback=None):
        if no_title is False:
            path = os.path.join(path, self.title + ".mp4")


        core.download(video=self, quality=quality, downloader=downloader, path=path, callback=callback)

class Client:
    def get_video(self, url):
        return Video(url)
