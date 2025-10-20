import os
import shutil
import subprocess
from pathlib import Path
from typing import Tuple

import librosa
import numpy as np
import yt_dlp

from karaoke_helper.helpers.typing import Spectrogram


def load_yt_url(artist: str, title: str) -> Path:
    out_name = f"{artist.replace(' ', '_')[-16:]}--{title.replace(' ', '_')[-16:]}.m4a"
    out = Path(f"cache/raw/{out_name}")
    if out.is_file():
        print("audio file is already cached")
        return out
    out.parent.mkdir(exist_ok=True, parents=True)

    yt_opts = {
        "cachedir": "cache/yt/",
        "default_search": "ytsearch",
        "noplaylist": True,
        "format": "m4a",
        "outtmpl": str(out),
        "postprocessors": [
            {  # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ],
    }
    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        error_code = ydl.download([f'"{artist}" "{title}"'])
    if error_code:
        print(f"failed to download audio: {error_code}")
    print("audio downloaded successfully")
    return out


def split_vocals(raw: Path) -> Tuple[Path, Path]:
    vocals = Path(f"cache/split/{raw.stem}.vocals.wav")
    instru = Path(f"cache/split/{raw.stem}.instru.wav")
    if vocals.is_file() and instru.is_file():
        print("split file already cached")
        return vocals, instru
    install_cmd = f"poetry install".split()
    run_cmd = f"poetry run spleeter separate -p spleeter:2stems -o cache/spleeter_out/ -f".split()
    run_cmd.append("{instrument}.{codec}")
    run_cmd.append(str(raw))
    env = os.environ.copy()
    if "VIRTUAL_ENV" in env:
        del env["VIRTUAL_ENV"]
    print(" ".join(install_cmd))
    subprocess.check_call(install_cmd, env=env)
    print(" ".join(run_cmd))
    subprocess.check_call(run_cmd, env=env)
    print("splitting done")
    vocals.parent.mkdir(exist_ok=True, parents=True)
    shutil.move("cache/spleeter_out/vocals.wav", vocals)
    shutil.move("cache/spleeter_out/accompaniment.wav", instru)
    return vocals, instru


def load_file_spectrogram(vocals: Path) -> Spectrogram:
    y, sr = librosa.load(vocals)
    return np.abs(librosa.stft(y))


def load_file_raw(vocals: Path) -> Tuple[np.ndarray, int]:
    return librosa.load(vocals)
