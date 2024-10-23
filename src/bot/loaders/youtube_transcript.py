from urllib.parse import parse_qs
from urllib.parse import urlparse

from youtube_transcript_api import NoTranscriptFound
from youtube_transcript_api import Transcript
from youtube_transcript_api import TranscriptList
from youtube_transcript_api import TranscriptsDisabled
from youtube_transcript_api import YouTubeTranscriptApi

DEFAULT_LANGUAGES = ["zh-TW", "zh-Hant", "zh", "zh-Hans", "ja", "en"]
ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_NETLOCS = {
    "youtu.be",
    "m.youtube.com",
    "youtube.com",
    "www.youtube.com",
    "www.youtube-nocookie.com",
    "vid.plus",
}


def parse_video_id(url: str) -> str | None:
    """Parse a YouTube URL and return the video ID if valid, otherwise None."""
    parsed_url = urlparse(url)

    if parsed_url.scheme not in ALLOWED_SCHEMES:
        return None

    if parsed_url.netloc not in ALLOWED_NETLOCS:
        return None

    path = parsed_url.path

    if path.endswith("/watch"):
        query = parsed_url.query
        parsed_query = parse_qs(query)
        if "v" in parsed_query:
            ids = parsed_query["v"]
            video_id = ids if isinstance(ids, str) else ids[0]
        else:
            return None
    else:
        path = parsed_url.path.lstrip("/")
        video_id = path.split("/")[-1]

    if len(video_id) != 11:  # Video IDs are 11 characters long
        return None

    return video_id


def load_youtube_transcript(url: str, languages: list[str] | None = None) -> str | None:
    languages = languages or DEFAULT_LANGUAGES

    video_id = parse_video_id(url)
    if not video_id:
        return None

    try:
        transcript_list: TranscriptList = YouTubeTranscriptApi.list_transcripts(video_id)
    except TranscriptsDisabled:
        return None

    try:
        transcript: Transcript = transcript_list.find_transcript(languages)
    except NoTranscriptFound:
        return None

    transcript_pieces: list[dict[str, str | float]] = transcript.fetch()

    return " ".join(str(transcript_piece.get("text", "")).strip() for transcript_piece in transcript_pieces)
