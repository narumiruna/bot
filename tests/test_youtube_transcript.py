from bot.loaders.youtube_transcript import load_youtube_transcript
from bot.loaders.youtube_transcript import parse_video_id


def test_load_valid_url_real():
    url = "https://youtu.be/Rz1Kujq73kM"
    result = load_youtube_transcript(url)
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_parse_video_id_valid():
    url = "https://youtu.be/Rz1Kujq73kM"
    video_id = parse_video_id(url)
    assert video_id == "Rz1Kujq73kM"


def test_parse_video_id_invalid_scheme():
    url = "ftp://youtu.be/Rz1Kujq73kM"
    video_id = parse_video_id(url)
    assert video_id is None


def test_parse_video_id_invalid_netloc():
    url = "https://invalidurl.com/watch?v=Rz1Kujq73kM"
    video_id = parse_video_id(url)
    assert video_id is None


def test_parse_video_id_invalid_path():
    url = "https://youtu.be/"
    video_id = parse_video_id(url)
    assert video_id is None


def test_parse_video_id_watch_path():
    url = "https://www.youtube.com/watch?v=Rz1Kujq73kM"
    video_id = parse_video_id(url)
    assert video_id == "Rz1Kujq73kM"
