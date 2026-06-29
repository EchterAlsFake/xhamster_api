import pytest
from ..api import Client, DownloadConfigHLS


@pytest.mark.asyncio
async def test_all_video():
    try:
        import av
    except (ModuleNotFoundError, ImportError):
        raise "Can't run tests without av installed!"

    client = Client()
    video = await client.get_video("https://xhamster.com/videos/stepmom-milf-try-on-panties-and-short-shorts-try-not-cum-xhWxerG")

    assert isinstance(video.title, str)
    assert isinstance(video.video_id, int)
    assert isinstance(video.m3u8_base_url, str)
    assert isinstance(video.likes, int)
    assert isinstance(video.dislikes, int)
    assert isinstance(video.categories, list)
    assert isinstance(video.tags, list)
    assert isinstance(video.pornstars, list)
    assert isinstance(video.rating_percentage, int)
    assert isinstance(video.thumbnail, str)
    assert isinstance(video.uploader_name, str)
    assert isinstance(video.uploader_subcribers, int)
    assert isinstance(video._uploader_tag_model, dict)


    config = DownloadConfigHLS(quality="worst", return_report=True)
    config_2 = DownloadConfigHLS(quality="worst", return_report=True, remux=True)

    status_1 = await video.download(config)
    assert status_1["status"] == "completed"

    status_2 = await video.download(config_2)
    assert status_2["status"] == "completed"

