import librosa
import numpy as np
import sounddevice as sd

from karaoke_helper.audio_processing.constants import SINGABLE_NOTE_FREQUENCIES
from karaoke_helper.audio_processing.pitch_tracker import \
    spectrogram_to_pitches
from karaoke_helper.helpers.sliding_buffer import SlidingBuffer
from karaoke_helper.ui.ui import UI


class Runner:
    def __init__(self, ui: UI):
        self.sample_rate = 44100  # Sample rate in Hz
        self.window_size = 2048  # Window size for STFT
        self.raw_audio_buffer = SlidingBuffer(
            self.window_size, 1, self.window_size * 255
        )
        self.notes_buffer = SlidingBuffer(700, len(SINGABLE_NOTE_FREQUENCIES), 700 * 4)
        self.ui = ui

    @staticmethod
    def shift_with_padding(array: np.ndarray, n: int, axis: int) -> np.ndarray:
        if axis == 0:
            return np.pad(array, ((n, 0), (0, 0)), mode="constant")[:-n, :]
        if axis == 1:
            return np.pad(array, ((0, 0), (n, 0)), mode="constant")[:, :-n]

    def run(self):
        def callback(indata: np.ndarray, frames, time, status):
            self.raw_audio_buffer.add(indata)
            s = np.abs(
                librosa.stft(self.raw_audio_buffer.get()[:, 0], n_fft=self.window_size)
            )
            pitches = spectrogram_to_pitches(s)
            pitches = pitches.mean(axis=0)
            self.notes_buffer.add(pitches[None, :])

        # Start the audio stream
        with sd.InputStream(callback=callback, channels=1, samplerate=self.sample_rate):
            while self.ui.is_running():
                self.ui.render_pitches(self.notes_buffer.get())
