import time
from typing import List

import librosa
import numpy as np
import sounddevice as sd

from karaoke_helper.audio_processing.constants import (
    UPSCALE_SINGABLE_NOTE_BOUNDARIES,
    UPSCALE_SINGABLE_NOTE_FREQUENCIES,
)
from karaoke_helper.audio_processing.lyrics_transcription import Transcript
from karaoke_helper.audio_processing.pitch_tracker import spectrogram_to_pitches
from karaoke_helper.helpers.sliding_buffer import SlidingBuffer
from karaoke_helper.helpers.typing import Pitches
from karaoke_helper.ui.ui import UI


class Runner:
    def __init__(self, ref_pitches: Pitches, transcript: Transcript, ui: UI):
        self.sample_rate = 44100  # Sample rate in Hz
        self.window_size = 2048  # Window size for STFT
        self.raw_audio_buffer = SlidingBuffer(
            self.window_size, 1, self.window_size * 255
        )
        self.note_buffer_size = 700
        self.notes_buffer = SlidingBuffer(
            self.note_buffer_size,
            len(UPSCALE_SINGABLE_NOTE_FREQUENCIES),
            self.note_buffer_size * 4,
        )
        self.live_note_times = SlidingBuffer(
            self.note_buffer_size, 1, self.note_buffer_size * 4
        )
        self.ui = ui
        self.ref_pitches = ref_pitches
        self.scroll_speed_s_per_screen = 10
        self.transcript = transcript

    @staticmethod
    def shift_with_padding(array: np.ndarray, n: int, axis: int) -> np.ndarray:
        if axis == 0:
            return np.pad(array, ((n, 0), (0, 0)), mode="constant")[:-n, :]
        if axis == 1:
            return np.pad(array, ((0, 0), (n, 0)), mode="constant")[:, :-n]

    def run(self):
        start = time.time()
        expected_time_between_samples = (
            self.scroll_speed_s_per_screen / self.note_buffer_size / 2
        )

        def callback(indata: np.ndarray, *args):
            callback_time = time.time() - start
            self.raw_audio_buffer.add(indata)
            s = np.abs(
                librosa.stft(self.raw_audio_buffer.get()[:, 0], n_fft=self.window_size)
            )
            if (
                callback_time - self.live_note_times.get()[-10, 0]
                > expected_time_between_samples * 10
            ):
                pitches = spectrogram_to_pitches(
                    s,
                    frequencies=UPSCALE_SINGABLE_NOTE_FREQUENCIES,
                    boundaries=UPSCALE_SINGABLE_NOTE_BOUNDARIES,
                )
                pitches = pitches.mean(axis=0)[None, :]
                self.notes_buffer.add(pitches)
                self.live_note_times.add(np.ones((len(pitches), 1)) * callback_time)

        # Start the audio stream
        with sd.InputStream(callback=callback, channels=1, samplerate=self.sample_rate):
            while self.ui.is_running():
                t = time.time() - start
                live_pitches = get_last_seconds_live(
                    self.notes_buffer.get(),
                    self.live_note_times.get()[:, 0],
                    t,
                    self.scroll_speed_s_per_screen / 2,
                )
                ref_pitches = get_time_slice(
                    self.ref_pitches,
                    t - self.scroll_speed_s_per_screen / 2,
                    t + self.scroll_speed_s_per_screen / 2,
                )
                self.ui.render(
                    live_pitches, ref_pitches, t, self.scroll_speed_s_per_screen
                )


def get_last_seconds_live(
    pitches: Pitches, note_times: np.ndarray, t: float, duration: float
):
    earliest_time = t - duration
    n = len(pitches)
    if earliest_time > note_times[0]:
        index = np.searchsorted(note_times, earliest_time)
    else:
        index = np.searchsorted(note_times, 0.01)
    res = pitches[index:]
    if note_times[-2] > 0:
        frame_per_seconds = (n - index) / (note_times[-1] - note_times[index])
        expected_frames = int(frame_per_seconds * duration)
        missing_frames = expected_frames - len(res)
        res = left_pad(res, missing_frames)
    return res


def get_time_slice(pitches: Pitches, start: float, end: float):
    total_recording_length = librosa.get_duration(S=pitches.T)
    frame_per_seconds = len(pitches) / total_recording_length
    start_frame = int(start * frame_per_seconds)
    end_frame = int(end * frame_per_seconds)
    missing_frames_start = -start_frame
    missing_frames_end = end_frame - len(pitches)
    res = pitches[max(0, start_frame) : end_frame]
    res = left_pad(res, missing_frames_start)
    res = right_pad(res, missing_frames_end)
    return res


def left_pad(pitches: Pitches, extra_frames: int):
    if extra_frames <= 0:
        return pitches
    return np.pad(pitches, ((extra_frames, 0), (0, 0)))


def right_pad(pitches: Pitches, extra_frames: int):
    if extra_frames <= 0:
        return pitches
    return np.pad(pitches, ((0, extra_frames), (0, 0)))
