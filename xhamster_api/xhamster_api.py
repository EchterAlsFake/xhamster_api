from __future__ import annotations
import os
import logging
import demjson3
import threading


from functools import cached_property
from urllib.parse import urlencode, quote
from base_api.modules.config import RuntimeConfig
from base_api.modules.errors import NetworkingError, BotProtectionDetected, UnknownError, InvalidProxy
from typing import Literal, AsyncGenerator, Any, Dict, List
from base_api.base import BaseCore, setup_logger, Helper
from curl_cffi import AsyncSession, Response
from base_api.modules.type_hints import DownloadReport

try:
    from modules.consts import *
    from modules.errors import *
    from modules.type_hints import callback_hint
except (ModuleNotFoundError, ImportError):
    from .modules.consts import *
    from .modules.errors import *
    from .modules.type_hints import callback_hint

try:
    import lxml
    parser = "lxml"
except (ModuleNotFoundError, ImportError):
    parser = "html.parser"


async def get_html_content(core: BaseCore, url: str) -> str | None:
    # What should I do here?
    try:
        content = await core.fetch(url)
        if isinstance(content, str):
            return content

        if isinstance(content, Response):
            if content.status_code == 404:
                raise NotFound(f"Server returned 404 for: {url}")

    except NetworkingError:
        raise NetworkError from NetworkingError

    except InvalidProxy:
        raise ProxyError from InvalidProxy

    except BotProtectionDetected:
        raise BotDetection from BotProtectionDetected

    except UnknownError:
        raise UnknownNetworkError from UnknownError


class Something(Helper):
    def __init__(self, soup: BeautifulSoup, url: str, core: BaseCore,
                 html_content: str):
        super().__init__(core, video_constructor=Video, log_level=logging.ERROR, alternative_constructor=Short)
        self.url = url
        self.html_content = html_content
        self.soup: BeautifulSoup = soup

    @classmethod
    async def init(cls, url: str, core: BaseCore, html_content: str | None = None) -> Something:
        if not html_content:
            response = await core.fetch(url)
            # Ensure we have a string for BeautifulSoup
            if response is None:
                html_content = ""
            elif not isinstance(response, str):
                html_content = getattr(response, "text", str(response))
            else:
                html_content = response

        soup = BeautifulSoup(html_content, parser)
        return cls(soup=soup, url=url, core=core, html_content=html_content)

    def _find_text(self, name: str, **kwargs) -> str:
        """Safely find a tag and return its stripped text, or an empty string."""
        tag = self.soup.find(name, **kwargs)
        return tag.text.strip() if tag else ""

    @cached_property
    def name(self) -> str:
        return self._find_text(
            "h1",
            class_="h3-bold-8643e primary-8643e landing-info__user-title"
        )

    @cached_property
    def subscribers_count(self) -> str:
        return self._find_text(
            "div",
            class_="body-8643e primary-8643e landing-info__metric-value"
        )

    @cached_property
    def videos_count(self) -> str:
        nodes = self.soup.find_all(
            "div",
            class_="body-8643e primary-8643e landing-info__metric-value"
        )
        return nodes[1].text.strip() if len(nodes) > 1 else ""

    @cached_property
    def total_views_count(self) -> str:
        nodes = self.soup.find_all(
            "div",
            class_="body-8643e primary-8643e landing-info__metric-value"
        )
        return nodes[2].text.strip() if len(nodes) > 2 else ""

    @cached_property
    def avatar_url(self) -> str:
        return REGEX_AVATAR.search(self.html_content).group(1)

    async def videos(self, pages: int = 2, videos_concurrency: int | None = None, pages_concurrency: int | None = None) -> AsyncGenerator[Video, None]:
        page_urls = [build_page_url(url=self.url, is_search=False, idx=page) for page in range(1, pages + 1)]
        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency
        assert videos_concurrency and pages_concurrency

        async for video in self.iterator(use_alternative_constructor=True, video_link_extractor=extractor_shorts, target_page_urls=page_urls,
                                 max_video_concurrency=videos_concurrency, max_page_concurrency=pages_concurrency):
            yield await video.init()

    @cached_property
    def get_information(self) -> Dict[str, str] | None:
        container = self.soup.find("div", class_="personalInfo-5360e")
        if not container:
            return None # No User Information present...

        li_tags = container.find_all("li")
        fortnite = self.soup.find_all("ul", class_="list-b51e4")
        if len(fortnite) > 1:
            li_tags.extend(fortnite[1].find_all("li"))

        dictionary = {}

        for li_tag in li_tags:
            divs = li_tag.find_all("div")
            if len(divs) >= 2:
                key = divs[0].text.strip()
                value = divs[1].text.strip()
                dictionary[key] = value

        return dictionary

    async def get_shorts(self, pages: int = 2, videos_concurrency: int = 2, pages_concurrency: int = 1) -> AsyncGenerator[Short, None]:
        if not self.url.endswith("/"):
            self.url += "/"

        self.url += "shorts"
        page_urls = [build_page_url(self.url, is_search=False, idx=page) for page in range(1, pages + 1)]
        async for short in self.iterator(use_alternative_constructor=True, video_link_extractor=extractor_shorts, target_page_urls=page_urls,
                                 max_video_concurrency=videos_concurrency, max_page_concurrency=pages_concurrency):
            yield await short.init()

class Channel(Something):
    pass


class Pornstar(Something):
    @cached_property
    def name(self) -> str:
        return self._find_text("h2", class_="h3-bold-8643e primary-8643e landing-info__user-title")


class Creator(Something):
    pass

class Short:
    def __init__(self, url: str, core: BaseCore, html_content: str | None = None):
        self.core = core
        self.url = url
        self.logger = setup_logger(name="XHamster API - [Short]")
        self.html_content = html_content

    async def init(self) -> Short:
        if not self.html_content:
            self.html_content = await get_html_content(core=self.core, url=self.url)
            assert self.html_content

        return self

    @cached_property
    def data(self) -> dict:
        assert self.html_content
        soup = BeautifulSoup(self.html_content, parser)
        script = soup.find("script", attrs={"id": "initials-script"}).text
        # Extract the JSON part after 'window.initials='
        json_text = script.split("window.initials=", 1)[-1].strip().rstrip(";")
        return demjson3.decode(json_text)

    @cached_property
    def title(self) -> str:
        return self.data.get('layoutPage', {}).get('momentProps', {}).get('title', '')

    @cached_property
    def author(self) -> str:
        author = self.data.get('layoutPage', {}).get('momentProps', {}).get('landing', {}).get('name')
        return str(author) if author else ""

    @cached_property
    def likes(self) -> int:
        likes = self.data.get('layoutPage', {}).get('momentProps', {}).get('ratingModel', {}).get('likes')
        return int(likes) if likes is not None else 0

    @cached_property
    def dislikes(self) -> int:
        dislikes = self.data.get('layoutPage', {}).get('momentProps', {}).get('ratingModel', {}).get('dislikes')
        return int(dislikes) if dislikes is not None else 0

    @cached_property
    def views(self) -> int:
        views = self.data.get('layoutPage', {}).get('momentProps', {}).get('views')
        return int(views) if views is not None else 0

    @cached_property
    def comments(self) -> int:
        comments = self.data.get('layoutPage', {}).get('momentProps', {}).get('comments')
        return int(comments) if comments is not None else 0

    @cached_property
    def duration(self) -> int:
        duration = self.data.get('xplayerSettings', {}).get('duration')
        return int(duration) if duration is not None else 0

    @cached_property
    def video_id(self) -> int:
        video_id = self.data.get('xplayerSettings', {}).get('videoId')
        if not video_id:
             video_id = self.data.get('layoutPage', {}).get('momentProps', {}).get('id')
        return int(video_id) if video_id is not None else 0

    @cached_property
    def created_at(self) -> int:
        created = self.data.get('layoutPage', {}).get('momentProps', {}).get('created')
        return int(created) if created is not None else 0

    @cached_property
    def tags(self) -> List[str]:
        tags = self.data.get('layoutPage', {}).get('momentProps', {}).get('tags', [])
        return [tag.get('name') for tag in tags if tag.get('name')]

    @cached_property
    def author_subscribers(self) -> int:
        subscribers = self.data.get('layoutPage', {}).get('momentProps', {}).get('landing', {}).get('subscribers')
        return int(subscribers) if subscribers is not None else 0

    @cached_property
    def author_logo(self) -> str:
        return self.data.get('layoutPage', {}).get('momentProps', {}).get('landing', {}).get('logo', '')

    @cached_property
    def author_link(self) -> str:
        return self.data.get('layoutPage', {}).get('momentProps', {}).get('landing', {}).get('link', '')

    @cached_property
    def thumb_url(self) -> str:
        return self.data.get('layoutPage', {}).get('momentProps', {}).get('thumbUrl', '')

    @cached_property
    def poster_url(self) -> str:
        return self.data.get('layoutPage', {}).get('momentProps', {}).get('posterUrl', '')

    @cached_property
    def m3u8_base_url(self) -> str:
        url = self.data.get('xplayerSettings', {}).get('sources', {}).get('hls', {}).get('h264', {}).get('url')
        if not url:
            url = self.data.get('layoutPage', {}).get('momentProps', {}).get('sources', {}).get('hls', {}).get('h264', {}).get('url')
        return str(url) if url else ""

    async def get_segments(self, quality: str | int) -> List[Any]:
        return await self.core.get_segments(self.m3u8_base_url, quality=quality)

    async def download(self, quality: str | int, path: str = "./", callback: callback_hint = None, no_title: bool = False, remux: bool = False,
                       callback_remux: callback_hint = None, start_segment: int = 0, stop_event: threading.Event | None = None,
                       segment_state_path: str | None = None, segment_dir: str | None = None,
                       return_report: bool = False, cleanup_on_stop: bool = True, keep_segment_dir: bool = False
                       ) -> bool | DownloadReport | None:
        """
        :param callback:
        :param quality:
        :param path:
        :param no_title:
        :param remux:
        :param callback_remux:
        :param start_segment:
        :param stop_event:
        :param segment_state_path:
        :param segment_dir:
        :param return_report:
        :param cleanup_on_stop:
        :param keep_segment_dir:
        :return:
        """

        if not no_title:
            path = os.path.join(path, f"{self.title}.mp4")


        return await self.core.download(video=self, quality=quality, path=path, callback=callback, remux=remux,
                                  callback_remux=callback_remux, start_segment=start_segment, stop_event=stop_event,
                                  segment_state_path=segment_state_path, segment_dir=segment_dir,
                                  return_report=return_report,
                                  cleanup_on_stop=cleanup_on_stop, keep_segment_dir=keep_segment_dir)


class Video:
    def __init__(self, url: str, core: BaseCore, html_content: str | None = None):
        self.core = core
        self.url = url
        self.logger = setup_logger(name="XHamster API - [Video]")
        self.html_content = html_content

    async def init(self) -> Video:
        if not self.html_content:
            self.html_content = await get_html_content(core=self.core, url=self.url)

        return self

    def enable_logging(self, log_file: str | None = None, level: int = logging.DEBUG, log_ip: str | None = None, log_port: int | None = None) -> None:
        self.logger = setup_logger(name="XHamster API - [Video]", level=level, log_file=log_file, http_ip=log_ip, http_port=log_port)

    @cached_property
    def title(self) -> str:
        return REGEX_TITLE.search(self.html_content).group(1)

    @cached_property
    def pornstars(self) -> List[str]:
        matches = REGEX_AUTHOR.findall(self.html_content)
        actual_pornstars = []
        for match in matches:
            actual_pornstars.append(match[1])

        return actual_pornstars

    @cached_property
    def thumbnail(self) -> str:
        return REGEX_THUMBNAIL.search(self.html_content).group(1)

    @cached_property
    def m3u8_base_url(self) -> str:
        url =  REGEX_M3U8.search(self.html_content).group(0)
        fixed_url = url.replace("\\/", "/")  # Fixing escaped slashes
        self.logger.debug(f"M3U8 URL: {fixed_url}")
        return fixed_url

    async def get_segments(self, quality: str | int) -> List[Any]:
        assert isinstance(self.core, BaseCore)
        return await self.core.get_segments(self.m3u8_base_url, quality=quality)

    async def download(self, quality: str | int, path: str = "./", callback: callback_hint = None
                       , no_title: bool = False, remux: bool = False,
                 callback_remux: callback_hint = None, start_segment: int = 0, stop_event: threading.Event | None = None,
                 segment_state_path: str | None = None, segment_dir: str | None = None,
                 return_report: bool = False, cleanup_on_stop: bool = True, keep_segment_dir: bool = False
                 ) -> bool | DownloadReport | None:
        """
        :param callback:
        :param quality:
        :param path:
        :param no_title:
        :param remux:
        :param callback_remux:
        :param start_segment:
        :param stop_event:
        :param segment_state_path:
        :param segment_dir:
        :param return_report:
        :param cleanup_on_stop:
        :param keep_segment_dir:
        :return:
        """

        if not no_title:
            path = os.path.join(path, f"{self.title}.mp4")

        assert isinstance(self.core, BaseCore)
        return await self.core.download(video=self, quality=quality, path=path, callback=callback, remux=remux,
                                  callback_remux=callback_remux, start_segment=start_segment, stop_event=stop_event,
                                  segment_state_path=segment_state_path, segment_dir=segment_dir,
                                  return_report=return_report,
                                  cleanup_on_stop=cleanup_on_stop, keep_segment_dir=keep_segment_dir)


class Client(Helper):
    def __init__(self, core: BaseCore = BaseCore(RuntimeConfig())):
        super().__init__(core=core, video_constructor=Video)
        self.core.initialize_session()
        assert isinstance(self.core.session, AsyncSession)
        self.core.session.headers.update(headers)

    async def get_video(self, url: str) -> Video:
        video = Video(url, core=self.core)
        return await video.init()

    async def get_pornstar(self, url: str) -> Pornstar:
        return await Pornstar.init(url=url, core=self.core)

    async def get_creator(self, url: str) -> Creator:
        return await Creator.init(url=url, core=self.core)

    async def get_channel(self, url: str) -> Channel:
        return await Channel.init(url=url, core=self.core)

    async def get_short(self, url: str) -> Short:
        short = Short(url, core=self.core)
        return await short.init()

    async def search_videos(self, query: str,
        minimum_quality: Literal["720p", "1080p", "2160p"] = "720p",
        sort_by: Literal["views", "newest", "best", "longest"] | None = None, # Empty string sorts by relevance

        category: Literal["german", "amateur", "18-year-old", "granny", "anal", "old-young", "mature",
        "mom", "milf", "big-tits", "big-natural-tits", "lesbian", "teen", "cum-in-mouth", "bdsm",
        "porn-for-women", "russian", "vintage", "hairy", "brutal-sex"] | List[str] | None = None ,
        vr: bool = False,
        full_length_only: bool = False,
        min_duration: Literal["2", "5", "10", "30", "40"] | None = None,
        date: Literal["latest", "weekly", "monthly", "yearly"] | None = None,
        production: Literal["studios", "creators"] | None = None,
        fps: Literal["30", "60"] | None = None,
        pages: int = 2, videos_concurrency: int | None = None, pages_concurrency: int | None = None,) -> AsyncGenerator[Video, None]:
        path = quote(str(query), safe="")  # e.g. "4k cats & dogs" -> "4k%20cats%20%26%20dogs"
        base = f"https://xhamster.com/search/"
        url = base + path

        videos_concurrency = videos_concurrency or self.core.configuration.videos_concurrency
        pages_concurrency = pages_concurrency or self.core.configuration.pages_concurrency

        params = {}

        if minimum_quality:
            params["quality"] = minimum_quality

        if sort_by:
            params["sort"] = sort_by

        if category:
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
        assert isinstance(videos_concurrency, int)
        assert isinstance(pages_concurrency, int)

        async for video in self.iterator(use_alternative_constructor=True, video_link_extractor=extractor_shorts, target_page_urls=page_urls,
                                 max_video_concurrency=videos_concurrency, max_page_concurrency=pages_concurrency):
            yield await video.init()
