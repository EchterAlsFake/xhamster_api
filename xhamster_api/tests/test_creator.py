import pytest
from ..api import Client


@pytest.mark.asyncio
async def test_creator():
    client = Client()
    creator = await client.get_creator("https://xhamster.com/creators/comatozze")
    assert isinstance(creator.name, str)
    assert isinstance(creator.subscribers_count, str)
    assert isinstance(creator.videos_count, str)
    assert isinstance(creator.total_views_count, str)
    assert isinstance(creator.avatar_url, str)
    assert isinstance(creator.get_information, dict)

    idx = 0
    async for result in creator.videos():
        idx += 1
        assert isinstance(result.video.title, str)

        if idx >= 3:
            break

    idx = 0
    async for result in creator.get_shorts():
        idx += 1
        assert isinstance(result.video.title, str)

        if idx >= 3:
            break
