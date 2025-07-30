from ..xhamster_api import Client

client = Client()
url = "https://ge.xhamster.com/videos/summer-dress-up-and-in-xh1bx0z"
video = client.get_video(url)

def test_title():
    assert isinstance(video.title, str)

def test_author():
    assert isinstance(video.thumbnail, str)

def test_pornstars():
    assert isinstance(video.pornstars, list)

def test_download_raw():
    assert video.download(quality="worst", downloader="threaded") is True

def test_download_remux():
    assert video.download(quality="best", downloader="threaded", remux=True) is True