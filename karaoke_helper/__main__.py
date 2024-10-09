import sys

from karaoke_helper.runner import Runner
from karaoke_helper.ui.ui import UI

from .audio_processing.pitch_tracker import spectrogram_to_pitches
from .audio_processing.song_loading import load_file, load_yt_url, split_vocals


def entrypoint():
    raw = load_yt_url(sys.argv[1])
    split = split_vocals(raw)
    s = load_file(split)
    pitches = spectrogram_to_pitches(s)
    runner = Runner(pitches, UI())
    runner.run()


if __name__ == "__main__":
    entrypoint()
