import sys
from pathlib import Path

import numpy as np
import pygame

from .audio_processing.pitch_tracker import spectrogram_to_pitches
from .audio_processing.song_loading import load_file, load_yt_url
from .ui.runner import Runner


def entrypoint():
    load_yt_url(sys.argv[1])
    # s = load_file(Path("vocals.wav"))
    # pitches = spectrogram_to_pitches(s)
    # img = pygame.surfarray.make_surface(np.flip(pitches, axis=1))
    # runner = Runner(img)
    # runner.run()


if __name__ == "__main__":
    entrypoint()
