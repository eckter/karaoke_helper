import sys

import numpy as np
import pygame

from .audio_processing.pitch_tracker import spectrogram_to_pitches
from .audio_processing.song_loading import load_file, load_yt_url, split_vocals
from .ui.runner import Runner


def entrypoint():
    raw = load_yt_url(sys.argv[1])
    split = split_vocals(raw)
    s = load_file(split)
    pitches = np.flip(spectrogram_to_pitches(s), axis=1)
    runner = Runner(pitches)
    runner.run()


if __name__ == "__main__":
    entrypoint()
