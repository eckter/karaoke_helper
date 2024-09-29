import librosa
import numpy as np
import subprocess
import shutil
import youtube_dl
import sys
from pathlib import Path

AudioSpectrogram = np.typing.ArrayLike


def load_yt_url(url: str) -> Path:
    video_info = youtube_dl.YoutubeDL().extract_info(
        url=url, download=False
    )
    out = Path(f"cache/raw/{video_info['title']}.mp3")
    if out.is_file():
        print("mp3 file is already cached")
        return out
    out.parent.mkdir(exists_ok=True)
    options = {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'outtmpl': str(out),
    }
    print(options)
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info["webpage_url"]])
    print("mp3 downloaded successfully")
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
