import pytest

from bot.loaders.youtube_transcript import YoutubeTranscriptLoader
from bot.loaders.youtube_transcript import parse_video_id


@pytest.fixture
def loader():
    return YoutubeTranscriptLoader()


def test_load_valid_url_real(loader):
    url = "https://youtu.be/3_Kv1VUWz1w"
    result = loader.load(url)
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    print(result)


def test_parse_video_id_valid():
    url = "https://youtu.be/3_Kv1VUWz1w"
    video_id = parse_video_id(url)
    assert video_id == "3_Kv1VUWz1w"


def test_parse_video_id_invalid_scheme():
    url = "ftp://youtu.be/3_Kv1VUWz1w"
    video_id = parse_video_id(url)
    assert video_id is None


def test_parse_video_id_invalid_netloc():
    url = "https://invalidurl.com/watch?v=3_Kv1VUWz1w"
    video_id = parse_video_id(url)
    assert video_id is None


def test_parse_video_id_invalid_path():
    url = "https://youtu.be/"
    video_id = parse_video_id(url)
    assert video_id is None


def test_parse_video_id_watch_path():
    url = "https://www.youtube.com/watch?v=3_Kv1VUWz1w"
    video_id = parse_video_id(url)
    assert video_id == "3_Kv1VUWz1w"
