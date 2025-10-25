import os
import logging
import traceback

from functools import cached_property
from urllib.parse import urlencode, quote
from base_api.modules.config import RuntimeConfig
from base_api.base import BaseCore, setup_logger, Helper
from typing import Optional, Literal, Generator, Union

try:
    from modules.consts import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *


class Something(Helper):
    def __init__(self, url: str, core: Optional[BaseCore] = None):
        super().__init__(core, video=Video, log_level=logging.ERROR, other=Short)
        self.url = url
        self.html_content = self.core.fetch(url)
        self.soup = BeautifulSoup(self.html_content, "lxml")

    @cached_property
    def name(self) -> str:
        return self.soup.find(
            "h1",
            class_="h3-bold-8643e primary-8643e landing-info__user-title"
        ).text.strip()

    @cached_property
    def subscribers_count(self) -> str:
        return self.soup.find(
            "div",
            class_="body-8643e primary-8643e landing-info__metric-value"
        ).text.strip()

    @cached_property
    def videos_count(self) -> str:
        return self.soup.find_all(
            "div",
            class_="body-8643e primary-8643e landing-info__metric-value"
        )[1].text.strip()

    @cached_property
    def total_views_count(self) -> str:
        return self.soup.find_all(
            "div",
            class_="body-8643e primary-8643e landing-info__metric-value"
        )[2].text.strip()

    @cached_property
    def avatar_url(self) -> str:
        return REGEX_AVATAR.search(self.html_content).group(1)

    def videos(self, pages: int = 2, videos_concurrency: int = None, pages_concurrency: int = None):
        page_urls = [build_page_url(url=self.url, is_search=False, idx=page) for page in range(1, pages + 1)]
        videos_concurrency = videos_concurrency or self.core.config.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.config.pages_concurrency
        yield from self.iterator(page_urls=page_urls, extractor=extractor_html, videos_concurrency=videos_concurrency,
                                 pages_concurrency=pages_concurrency)

    @cached_property
    def get_information(self) -> dict | None:
        container = self.soup.find("div", class_="personalInfo-5360e")
        if not container:
            return None # No User Information present...

        li_tags = container.find_all("li")
        fortnite = self.soup.find_all("ul", class_="list-b51e4")
        li_tags.extend(fortnite[1].find_all("li"))

        dictionary = {}

        for li_tag in li_tags:
            divs = li_tag.find_all("div")
            key = divs[0].text.strip()
            value = divs[1].text.strip()
            dictionary[key] = value

        return dictionary

    def get_shorts(self, pages: int = 2, videos_concurrency: int = 2, pages_concurrency: int = 1):
        if not self.url.endswith("/"):
            self.url += "/"

        self.url += "shorts"
        page_urls = [build_page_url(self.url, is_search=False, idx=page) for page in range(1, pages + 1)]
        yield from self.iterator(other_return=True, extractor=extractor_shorts, page_urls=page_urls,
                                 videos_concurrency=videos_concurrency, pages_concurrency=pages_concurrency)

class Channel(Something):
    pass


class Pornstar(Something):
    pass


class Creator(Something):
    pass

class Short:
    def __init__(self, url: str, core: Optional[BaseCore] = None):
        self.core = core
        self.url = url
        self.logger = setup_logger(name="XHamster API - [Short]")
        self.content = self.core.fetch(self.url)

    @cached_property
    def title(self) -> str:
        return REGEX_TITLE.search(self.content).group(1)

    @cached_property
    def author(self) -> str:
        return REGEX_AUTHOR_SHORTS.search(self.content).group(1)

    @cached_property
    def likes(self) -> int:
        return int(REGEX_LIKES_SHORTS.search(self.content).group(1))

    @cached_property
    def m3u8_base_url(self) -> str:
        return REGEX_M3U8.search(self.content).group(0)

    def get_segments(self) -> list:
        return self.core.get_segments(self.m3u8_base_url, quality="best") # Why would you download it not in the best quality like seriously...

    def download(self, quality: Union[int, str], downloader, path="./", no_title = False, callback=None, remux: bool = False,
                 remux_callback = None) -> bool:
        if no_title is False:
            path = os.path.join(path, self.title + ".mp4")

        try:
            self.core.download(video=self, quality=quality, downloader=downloader, path=path, callback=callback,
                           remux=remux, callback_remux=remux_callback)
            return True

        except Exception:
            error = traceback.format_exc()
            print(error)
            self.logger.error(error)
            return False


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
            print(error)
            self.logger.error(error)
            return False


class Client(Helper):
    def __init__(self, core: Optional[BaseCore] = None):
        super().__init__(core, video=Video)
        self.core = core or BaseCore(config=RuntimeConfig())
        self.core.initialize_session()
        self.core.session.headers.update(headers)

    def get_video(self, url: str) -> Video:
        return Video(url, core=self.core)

    def get_pornstar(self, url: str) -> Pornstar:
        return Pornstar(url, core=self.core)

    def get_creator(self, url: str) -> Creator:
        return Creator(url, core=self.core)

    def get_channel(self, url: str) -> Channel:
        return Channel(url, core=self.core)

    def get_short(self, url: str) -> Short:
        return Short(url, core=self.core)

    def search_videos(self, query: str,
        minimum_quality: Literal["720p", "1080p", "2160p"] = "720p",
        sort_by: Literal["views", "newest", "best", "longest"] = "", # Empty string sorts by rlevance

        category: Literal["german", "amateur", "18-year-old", "granny", "anal", "old-young", "mature",
        "mom", "milf", "big-tits", "big-natural-tits", "lesbian", "teen", "cum-in-mouth", "bdsm",
        "porn-for-women", "russian", "vintage", "hairy", "brutal-sex"] = "",
        vr: bool = False,
        full_length_only: bool = False,
        min_duration: Literal["2", "5", "10", "30", "40"] = "",
        date: Literal["latest", "weekly", "monthly", "yearly"] = "",
        production: Literal["studios", "creators"] = "",
        fps: Literal["30", "60"] = "",
        pages: int = 2, videos_concurrency: int = None, pages_concurrency: int = None,) -> Generator[Video, None, None]:
        path = quote(str(query), safe="")  # e.g. "4k cats & dogs" -> "4k%20cats%20%26%20dogs"
        base = f"https://xhamster.com/search/"
        url = base + path

        videos_concurrency = videos_concurrency or self.core.config.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.config.pages_concurrency

        params = {}

        if minimum_quality:
            params["quality"] = minimum_quality

        if sort_by:
            params["sort"] = sort_by

        if isinstance(category, list) and category:
            params["cats"] = category

        if vr:
            params["format"] = "vr"

        if full_length_only:
            params["length"] = "full"

        if min_duration:
            params["min-duration"] = min_duration  # note: += (don’t overwrite the URL)

        if date:
            params["date"] = date

        if production:
            params["prod"] = production

        if fps:
            params["fps"] = fps

        query_string = urlencode(params, doseq=True)
        final_url = f"{url}?{query_string}" if query_string else url
        page_urls = [build_page_url(url=final_url, is_search=True, idx=page) for page in range(1, pages + 1)]
        yield from self.iterator(page_urls=page_urls, extractor=extractor_html, videos_concurrency=videos_concurrency,
                                   pages_concurrency=pages_concurrency)


