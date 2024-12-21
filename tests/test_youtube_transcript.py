from bot.loaders.v2.youtube import parse_video_id


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
