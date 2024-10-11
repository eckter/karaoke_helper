import librosa
import numpy as np

from ..helpers.typing import Pitches, Spectrogram
from .constants import (
    SINGABLE_NOTE_BOUNDARIES,
    SINGABLE_NOTE_FREQUENCIES,
    UPSCALE_SINGABLE_NOTE_BOUNDARIES,
    UPSCALE_SINGABLE_NOTE_FREQUENCIES,
)


def audio_to_pitches(raw_audio: np.ndarray) -> Pitches:
    return spectrogram_to_pitches(np.abs(librosa.stft(raw_audio)))


def spectrogram_to_pitches(
    spectrogram: Spectrogram,
    frequencies: np.ndarray = SINGABLE_NOTE_FREQUENCIES,
    boundaries: np.ndarray = SINGABLE_NOTE_BOUNDARIES,
) -> Pitches:
    pitches, magnitudes = librosa.piptrack(
        S=spectrogram,
        fmin=frequencies[0],
        fmax=frequencies[-1],
    )
    n_notes = len(frequencies)
    indices = np.searchsorted(boundaries, pitches.T)
    out = np.array(
        [
            np.bincount(idx, weights=weights, minlength=n_notes)
            for (idx, weights) in zip(indices, magnitudes.T)
        ]
    )
    return out
