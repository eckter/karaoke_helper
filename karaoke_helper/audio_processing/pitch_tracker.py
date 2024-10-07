import librosa
import numpy as np

from ..helpers.typing import Pitches, Spectrogram
from .constants import SINGABLE_NOTE_BOUNDARIES, SINGABLE_NOTE_FREQUENCIES


def spectrogram_to_pitches(spectrogram: Spectrogram) -> Pitches:
    pitches, magnitudes = librosa.piptrack(
        S=spectrogram,
        fmin=SINGABLE_NOTE_FREQUENCIES[0],
        fmax=SINGABLE_NOTE_FREQUENCIES[-1],
    )
    n_notes = len(SINGABLE_NOTE_FREQUENCIES)
    indices = np.searchsorted(SINGABLE_NOTE_BOUNDARIES, pitches.T)
    out = np.array(
        [
            np.bincount(idx, weights=weights, minlength=n_notes)
            for (idx, weights) in zip(indices, magnitudes.T)
        ]
    )
    return out
