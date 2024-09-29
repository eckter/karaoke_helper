import librosa
import numpy as np

from .song_loading import AudioSpectrogram


def spectrogram_to_pitches(S: AudioSpectrogram) -> np.typing.ArrayLike:
    pitches, magnitudes = librosa.piptrack(S=S)

    mult = 10
    max_freq = 2000
    n = pitches.shape[1]
    out = np.zeros((n, int(max_freq / mult)))
    for t in range(n):
        ps = pitches[:, t]
        ms = magnitudes[:, t]
        for p, m in zip(ps, ms):
            if p <= max_freq:
                out[t, int(p / mult)] = m
    return out
