import functools
import os
import subprocess
import tempfile

import numpy as np
import whisper
import yt_dlp

try:
    import mlx_whisper  # noqa: F401

    _mlx_whisper_installed = True
except ImportError:
    _mlx_whisper_installed = False


def get_ffmpeg_path_from_env() -> str:
    return os.getenv("FFMPEG_PATH", "/opt/homebrew/bin/ffmpeg")


def ytdlp_download(url: str) -> str:
    ffmpeg_path = get_ffmpeg_path_from_env()

    filename = tempfile.mktemp()

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": filename,
        "ffmpeg_location": ffmpeg_path,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename + ".mp3"


def load_audio(file: str, sr: int = 16000):
    """
    Open an audio file and read as mono waveform, resampling as necessary

    Parameters
    ----------
    file: str
        The audio file to open

    sr: int
        The sample rate to resample the audio if necessary

    Returns
    -------
    A NumPy array containing the audio waveform, in float32 dtype.
    """
    ffmpeg_path = get_ffmpeg_path_from_env()

    # This launches a subprocess to decode audio while down-mixing
    # and resampling as necessary.  Requires the ffmpeg CLI in PATH.
    # fmt: off
    cmd = [
        ffmpeg_path,
        "-nostdin",
        "-threads", "0",
        "-i", file,
        "-f", "s16le",
        "-ac", "1",
        "-acodec", "pcm_s16le",
        "-ar", str(sr),
        "-"
    ]
    # fmt: on
    try:
        out = subprocess.run(cmd, capture_output=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

    return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0


@functools.cache
def _load_whisper_model() -> whisper.Whisper:
    return whisper.load_model("tiny")


def _transcribe(audio: np.ndarray) -> dict:
    if _mlx_whisper_installed:
        return mlx_whisper.transcribe(audio, path_or_hf_repo="mlx-community/whisper-tiny")

    model = _load_whisper_model()
    return model.transcribe(audio)


def load_video_transcript(url: str) -> str | None:
    f = ytdlp_download(url)
    audio = load_audio(f)
    result = _transcribe(audio)
    return result.get("text", "")
