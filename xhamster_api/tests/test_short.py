import pytest
from ..api import Client, DownloadConfigHLS


@pytest.mark.asyncio
async def test_short():
    try:
        import av
    except:
        raise "Can't run without AV"

    client = Client()
    short = await client.get_short("https://xhamster.com/shorts/teen-jerks-pussy-shower-xhecgTc")


    assert isinstance(short.title, str)
    assert isinstance(short.author, str)
    assert isinstance(short.likes, int)
    assert isinstance(short.dislikes, int)
    assert isinstance(short.views, int)
    assert isinstance(short.comments, int)
    assert isinstance(short.duration, int)
    assert isinstance(short.video_id, int)
    assert isinstance(short.created_at, int)
    assert isinstance(short.tags, list)
    assert isinstance(short.author_subscribers, int)
    assert isinstance(short.author_logo, str)
    assert isinstance(short.author_link, str)
    assert isinstance(short.thumb_url, str)
    assert isinstance(short.poster_url, str)
    assert isinstance(short.m3u8_base_url, str)

    config = DownloadConfigHLS(quality="best", return_report=True)
    result = await short.download(config)
    assert result.status == "completed"


