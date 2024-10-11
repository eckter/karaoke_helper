from typing import List

import numpy as np
import simpleaudio as sa


class Playback:
    def __init__(self, audio: np.ndarray, sr: int):
        audio *= 32767 / max(abs(audio))
        audio = audio.astype(np.int16)
        self.audio = audio
        self.sr = sr

    def start(self):
        sa.play_buffer(self.audio, 1, 2, self.sr)


class Playbacks:
    def __init__(self, playbacks: List[Playback]):
        self.playbacks = playbacks

    def start(self):
        for p in self.playbacks:
            p.start()
