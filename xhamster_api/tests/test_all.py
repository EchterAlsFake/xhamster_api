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

@pytest.fixture
def client() -> Client:
    return Client()

@pytest.mark.asyncio
async def test_video_attributes(client):
    v = await client.get_video(url=urls["video"])
    assert isinstance(v.title, str) and v.title.strip()
    assert isinstance(v.pornstars, list) and all(isinstance(x, str) and x for x in v.pornstars)
    assert isinstance(v.thumbnail, str) and v.thumbnail.startswith("http")
    assert isinstance(v.m3u8_base_url, str) and v.m3u8_base_url.endswith(".m3u8")

@pytest.mark.asyncio
async def test_short_attributes(client):
    s = await client.get_short(url=urls["short"])
    assert isinstance(s.title, str) and s.title.strip()
    assert isinstance(s.author, str) and s.author.strip()
    assert isinstance(s.likes, int) and s.likes >= 0
    assert isinstance(s.m3u8_base_url, str) and s.m3u8_base_url.endswith(".m3u8")
    assert isinstance(s.video_id, int)
    assert isinstance(s.created_at, int)
    assert isinstance(s.views, int)
    assert isinstance(s.dislikes, int)
    assert isinstance(s.comments, int)
    assert isinstance(s.duration, int)
    assert isinstance(s.tags, list)
    assert isinstance(s.author_subscribers, int)
    assert isinstance(s.author_logo, str)
    assert isinstance(s.author_link, str)

@pytest.mark.asyncio
async def test_channel_attributes(client):
    ch = await client.get_channel(url=urls["channel"])
    assert isinstance(ch.name, str) and ch.name.strip()
    assert isinstance(ch.subscribers_count, str) and ch.subscribers_count.strip()
    assert isinstance(ch.videos_count, str) and ch.videos_count.strip()
    assert isinstance(ch.total_views_count, str) and ch.total_views_count.strip()

@pytest.mark.asyncio
async def test_pornstar_attributes(client):
    ps = await client.get_pornstar(url=urls["pornstar"])
    assert isinstance(ps.name, str) and ps.name.strip()
    assert isinstance(ps.subscribers_count, str) and ps.subscribers_count.strip()
    assert isinstance(ps.videos_count, str) and ps.videos_count.strip()
    assert isinstance(ps.total_views_count, str) and ps.total_views_count.strip()

@pytest.mark.asyncio
async def test_creator_attributes(client):
    cr = await client.get_creator(url=urls["creator"])
    assert isinstance(cr.name, str)
    assert isinstance(cr.subscribers_count, str)
    assert isinstance(cr.videos_count, str)
    assert isinstance(cr.total_views_count, str)

@pytest.mark.asyncio
async def test_search_videos_returns_generator(client):
    gen = client.search_videos(query="comatozze")  # placeholder query for now
    assert isinstance(gen, types.AsyncGeneratorType)
