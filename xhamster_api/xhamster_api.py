import os
import traceback

from httpx import Response
from base_api import BaseCore
from bs4 import BeautifulSoup
from functools import cached_property
from base_api.base import setup_logger
from urllib.parse import urlencode, quote
from base_api.modules.config import RuntimeConfig
from typing import Optional, Literal, Generator, Union
from concurrent.futures import as_completed, ThreadPoolExecutor

try:
    from modules.consts import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *


class ErrorVideo:
    """Drop-in-ish stand-in that raises when accessed."""
    def __init__(self, url: str, err: Exception):
        self.url = url
        self._err = err

    def __getattr__(self, _):
        # Any attribute access surfaces the original error
        raise self._err



class Helper: # ChatGPT cooked not gonna lie
    def __init__(self, core: BaseCore):
        super().__init__()
        self.core = core
        self.url: Optional[str] = None

        # controls how iterator behaves
        self.is_search: bool = False          # True only for search mode
        self.pre_html: Optional[str] = None   # first-page HTML (for Something/*)

    def _get_video(self, url: str):
        return Video(url, core=self.core)

    def _make_video_safe(self, url: str):
        try:
            return Video(url, core=self.core)
        except Exception as e:
            return ErrorVideo(url, e)

    def _get_short(self, url: str):
        return Short(url, core=self.core)

    def _page_url(self, idx: int) -> Optional[str]:
        """
        Compute the URL to fetch for a given page index.

        SEARCH MODE:
            - always fetch ?page={idx}
        SOMETHING MODE (Channel/Pornstar/Creator):
            - idx == 0: use pre-fetched HTML (return None so caller won't fetch)
            - idx == 1: skip (duplicate of first page) -> return "" to signal skip
            - idx >= 2: fetch f"{base}/{idx}"
        """
        if self.url is None:
            return ""

        if self.is_search:
            # query-string pagination
            joiner = "&" if "?" in self.url else "?"
            return f"{self.url}{joiner}page={idx}"

        # non-search: special first page handling
        if idx == 0:
            return None  # signal: use self.pre_html once

        if idx == 1:
            return ""    # signal: skip (same as first page on this site)

        return f"{self.url}/{idx}"

    def _extract_video_links(self, html: str, shorts) -> list[str]:
        soup = BeautifulSoup(html, "html.parser")
        if not shorts:
            nodes = soup.find_all(
            "a",
            class_="video-thumb__image-container role-pop thumb-image-container"
        )

        else:
            nodes = soup.find_all("a",
                                  class_="imageContainer-a870e role-pop thumb-image-container thumb-image-container--moment")


        return [n.get("href") for n in nodes if n and n.get("href")]

    def iterator(self, pages: int = 0, max_workers: int = 20, shorts: bool = False):
        # 0 means “as many as practical” -> cap to a sane large number
        if pages == 0:
            pages = 99

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for idx in range(pages):
                page_url = self._page_url(idx)

                if page_url is None:
                    # use pre-fetched HTML exactly once (idx == 0 in Something/* mode)
                    content = self.pre_html
                elif page_url == "":
                    # explicit skip (idx == 1 in Something/* mode)
                    continue
                else:
                    content = self.core.fetch(page_url)
                    if isinstance(content, Response):
                        break  # 404 or no more content...

                if not content:
                    continue

                # --- Parse and schedule video creation ---
                video_links = self._extract_video_links(content, shorts)
                if not video_links:
                    if self.is_search:
                        continue
                    else:
                        break

                if not shorts:
                    futures = [executor.submit(self._make_video_safe, v) for v in video_links]

                else:
                    futures = [executor.submit(self._get_short, url) for url in video_links]

                for fut in as_completed(futures):
                    yield fut.result()


class Something(Helper):
    def __init__(self, url: str, core: Optional[BaseCore] = None):
        if core is None:
            raise ValueError("core must be provided")
        super().__init__(core)
        self.url = url
        self.is_search = False  # explicit
        # pre-fetch: this page already contains the first batch of videos
        self.html_content = self.core.fetch(url)
        self.pre_html = self.html_content
        self.soup = BeautifulSoup(self.html_content, "html.parser")

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

    def videos(self, pages: int = 2, max_workers: int = 20):
        # idx==0 -> use pre_html
        # idx==1 -> skip (same page)
        # idx>=2 -> fetch f"{url}/{idx}"
        yield from self.iterator(pages=pages, max_workers=max_workers)

    @cached_property
    def get_information(self) -> dict:
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

    def get_shorts(self):
        if not self.url.endswith("/"):
            self.url += "/"

        self.url += "shorts"
        yield from self.iterator(shorts=True)

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
        super().__init__(core)
        self.core = core or BaseCore(config=RuntimeConfig())
        self.core.initialize_session(headers)

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
                      pages: int = 2,
                      max_workers: int = 20) -> Generator[Video, None, None]:
        path = quote(str(query), safe="")  # e.g. "4k cats & dogs" -> "4k%20cats%20%26%20dogs"
        base = f"https://xhamster.com/search/"
        url = base + path

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

        # Use Helper in search mode
        helper = Helper(self.core)  # or however you construct it in your codebase
        helper.url = final_url
        helper.is_search = True  # critical: enables ?page= style
        helper.pre_html = None  # not used for search

        yield from helper.iterator(pages=pages, max_workers=max_workers)
