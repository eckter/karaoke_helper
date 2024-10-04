import librosa
import numpy as np

from .constants import SINGABLE_NOTE_FREQUENCIES
from .song_loading import AudioSpectrogram


def spectrogram_to_pitches(spectrogram: AudioSpectrogram) -> np.typing.ArrayLike:
    pitches, magnitudes = librosa.piptrack(
        S=spectrogram,
        fmin=SINGABLE_NOTE_FREQUENCIES[0],
        fmax=SINGABLE_NOTE_FREQUENCIES[-2],
    )
    n_notes = len(SINGABLE_NOTE_FREQUENCIES)
    indices = np.searchsorted(SINGABLE_NOTE_FREQUENCIES, pitches.T)
    out = np.array(
        [
            np.bincount(idx, weights=weights, minlength=n_notes)
            for (idx, weights) in zip(indices, magnitudes.T)
        ]
    )
    return out
