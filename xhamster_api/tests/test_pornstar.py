import pytest
from ..api import Client


@pytest.mark.asyncio
async def test_pornstar():
    client = Client()
    pornstar = await client.get_pornstar("https://xhamster.com/pornstars/polly-yangs")
    assert isinstance(pornstar.name, str)
    assert isinstance(pornstar.subscribers_count, str)
    assert isinstance(pornstar.videos_count, str)
    assert isinstance(pornstar.total_views_count, str)
    assert isinstance(pornstar.avatar_url, str)
    assert isinstance(pornstar.get_information, dict)

    idx = 0
    async for result in pornstar.videos():
        idx += 1
        assert isinstance(result.video.title, str)

        if idx >= 3:
            break


    idx = 0
    async for result in pornstar.get_shorts():
        idx += 1
        assert isinstance(result.video.title, str)

        if idx >= 3:
            break

