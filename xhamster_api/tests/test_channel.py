import pytest
from ..api import Client


@pytest.mark.asyncio
async def test_channel():
    client = Client()
    channel = await client.get_channel("https://xhamster.com/channels/brazzers")
    assert isinstance(channel.name, str)
    assert isinstance(channel.subscribers_count, str)
    assert isinstance(channel.videos_count, str)
    assert isinstance(channel.total_views_count, str)
    assert isinstance(channel.avatar_url, str)


    idx = 0
    async for result in channel.videos():
        idx += 1
        assert isinstance(result.video.title, str)

        if idx >= 3:
            break

    idx = 0
    async for result in channel.get_shorts():
        idx += 1
        assert isinstance(result.video.title, str)

        if idx >= 3:
            break
