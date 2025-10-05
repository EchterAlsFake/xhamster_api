import pytest
import types

# Import the classes under test from the user-provided module text.
# In a real project you'd do: from yourpackage.xham import Client, Video, Short, Channel, Pornstar, Creator, ErrorVideo
# For this snippet assume they are available in the test context.
from ..xhamster_api import Client, Video, Short, Channel, Pornstar, Creator, BaseCore

urls = {
    "video": "https://ge.xhamster.com/videos/shy-scared-fucking-beautiful-dumb-whores-1943069",
    "short": "https://ge.xhamster.com/moments/undress-press-confess-xhdhRqY",
    "channel": "https://ge.xhamster.com/channels/brazzers",
    "pornstar": "https://ge.xhamster.com/pornstars/tejashwini",
    "creator": "https://ge.xhamster.com/pornstars/tiffany-montavani"
}


# ---- Tests -------------------------------------------------------------------


core = BaseCore()

def test_video_attributes():
    v = Video(urls["video"], core)
    assert isinstance(v.title, str) and v.title.strip()
    assert isinstance(v.pornstars, list) and all(isinstance(x, str) and x for x in v.pornstars)
    assert isinstance(v.thumbnail, str) and v.thumbnail.startswith("http")
    assert isinstance(v.m3u8_base_url, str) and v.m3u8_base_url.endswith(".m3u8")


def test_short_attributes():
    s = Short(urls["short"], core)
    assert isinstance(s.title, str) and s.title.strip()
    assert isinstance(s.author, str) and s.author.strip()
    assert isinstance(s.likes, int) and s.likes >= 0
    assert isinstance(s.m3u8_base_url, str) and s.m3u8_base_url.endswith(".m3u8")


def test_channel_attributes():
    ch = Channel(urls["channel"], core)
    assert isinstance(ch.name, str) and ch.name.strip()
    assert isinstance(ch.subscribers_count, str) and ch.subscribers_count.strip()
    assert isinstance(ch.videos_count, str) and ch.videos_count.strip()
    assert isinstance(ch.total_views_count, str) and ch.total_views_count.strip()


def test_pornstar_attributes():
    ps = Pornstar(urls["pornstar"], core)
    assert isinstance(ps.name, str) and ps.name.strip()
    assert isinstance(ps.subscribers_count, str) and ps.subscribers_count.strip()
    assert isinstance(ps.videos_count, str) and ps.videos_count.strip()
    assert isinstance(ps.total_views_count, str) and ps.total_views_count.strip()


def test_creator_attributes():
    cr = Creator(urls["creator"], core)
    assert isinstance(cr.name, str) and cr.name.strip()
    assert isinstance(cr.subscribers_count, str) and cr.subscribers_count.strip()
    assert isinstance(cr.videos_count, str) and cr.videos_count.strip()
    assert isinstance(cr.total_views_count, str) and cr.total_views_count.strip()


def test_client_getters_return_correct_types():
    c = Client()
    assert isinstance(c.get_video(urls["video"]), Video)
    assert isinstance(c.get_short(urls["short"]), Short)
    assert isinstance(c.get_channel(urls["channel"]), Channel)
    assert isinstance(c.get_pornstar(urls["pornstar"]), Pornstar)
    assert isinstance(c.get_creator(urls["creator"]), Creator)


def test_search_videos_returns_generator():
    c = Client(core=core)
    gen = c.search_videos(query="comatozze")  # placeholder query for now
    assert isinstance(gen, types.GeneratorType)
