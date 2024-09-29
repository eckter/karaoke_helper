import librosa
import numpy as np
import subprocess
import shutil
import yt_dlp
import sys
from pathlib import Path

AudioSpectrogram = np.typing.ArrayLike


def load_yt_url(url: str) -> Path:
    out_name = "".join(c for c in url if c.isalnum()) + ".m4a"
    out_name = out_name[-32:]
    out = Path(f"cache/raw/{out_name}")
    if out.is_file():
        print("mp3 file is already cached")
        return out
    out.parent.mkdir(exist_ok=True)

    yt_opts = {
        "cachedir": "cache/yt/",
        "format": "m4a",
        "outtmpl": str(out),
        "postprocessors": [{  # Extract audio using ffmpeg
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
        }],
    }
    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        error_code = ydl.download(url)
    if error_code:
        print(f"failed to download audio: {error_code}")
    print("audio downloaded successfully")
    return out


def split_mp3_vocals(raw: Path) -> Path:
    out = Path(f"cache/split/{raw.name}")
    if out.is_file():
        print("split file already cached")
        return out
    cmd = f"python -m spleeter separate -p spleeter:2stems -o cache/spleeter_out/ -f".split()
    cmd.append("{instrument}.{codec}")
    cmd.append(str(raw))
    print(" ".join(cmd))
    subprocess.check_call(cmd)
    shutil.copy("cache/spleeter_out/vocals.wav", out)
    return out


def load_file(vocals: Path) -> AudioSpectrogram:
    y, sr = librosa.load(vocals, duration=20)
    return np.abs(librosa.stft(y))
