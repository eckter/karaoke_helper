import os
import shutil
import subprocess
from pathlib import Path

import librosa
import numpy as np
import yt_dlp

from karaoke_helper.helpers.typing import Spectrogram


def load_yt_url(url: str) -> Path:
    out_name = "".join(c for c in url if c.isalnum()) + ".m4a"
    out_name = out_name[-32:]
    out = Path(f"cache/raw/{out_name}")
    if out.is_file():
        print("audio file is already cached")
        return out
    out.parent.mkdir(exist_ok=True)

    yt_opts = {
        "cachedir": "cache/yt/",
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
        error_code = ydl.download(url)
    if error_code:
        print(f"failed to download audio: {error_code}")
    print("audio downloaded successfully")
    return out


def split_vocals(raw: Path, spleeter_path: Path = Path("spleeter")) -> Path:
    out = Path(f"cache/split/{raw.stem}.wav")
    if out.is_file():
        print("split file already cached")
        return out
    if not spleeter_path.is_dir():
        raise RuntimeError(
            "Missing spleeter install: run `git submodule update --recursive`"
        )
    install_cmd = f"poetry -C {spleeter_path} install".split()
    run_cmd = f"poetry -C {spleeter_path} run spleeter separate -p spleeter:2stems -o cache/spleeter_out/ -f".split()
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
    out.parent.mkdir(exist_ok=True)
    shutil.copy("cache/spleeter_out/vocals.wav", out)
    return out


def load_file(vocals: Path) -> Spectrogram:
    y, sr = librosa.load(vocals, duration=20)
    return np.abs(librosa.stft(y))
