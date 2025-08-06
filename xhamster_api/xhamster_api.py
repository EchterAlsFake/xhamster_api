import os
import traceback

from typing import Optional
from base_api import BaseCore
from functools import cached_property
from base_api.base import setup_logger
from base_api.modules.config import RuntimeConfig

try:
    from modules.consts import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *


class Video:
    def __init__(self, url, core: Optional[BaseCore] = None):
        self.core = core
        self.url = url
        self.logger = setup_logger(name="XHamster API - [Video]")
        self.content = self.core.fetch(self.url)

    def enable_logging(self, log_file: str = None, level=None, log_ip: str = None, log_port: int = None):
        self.logger = setup_logger(name="XHamster API - [Video]", level=level, log_file=log_file, http_ip=log_ip, http_port=log_port)

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

    def download(self, quality, downloader, path="./", no_title = False, callback=None, remux: bool = False,
                 remux_callback = None) -> bool:
        if no_title is False:
            path = os.path.join(path, self.title + ".mp4")

        try:
            self.core.download(video=self, quality=quality, downloader=downloader, path=path, callback=callback,
                           remux=remux, callback_remux=remux_callback)
            return True

        except Exception:
            error = traceback.format_exc()
            self.logger.error(error)
            return False


class Client:
    def __init__(self, core: Optional[BaseCore] = None):
        self.core = core or BaseCore(config=RuntimeConfig())
        self.core.initialize_session(headers)

    def get_video(self, url):
        return Video(url, core=self.core)
