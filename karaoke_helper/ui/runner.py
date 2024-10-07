import librosa
import numpy as np
import pygame
import sounddevice as sd

from karaoke_helper.audio_processing.constants import SINGABLE_NOTE_FREQUENCIES
from karaoke_helper.audio_processing.pitch_tracker import spectrogram_to_pitches
from karaoke_helper.helpers.sliding_buffer import SlidingBuffer


# Code architecture is very bare-bone and quite clunky there,
# this is just an early prototype. Eventually we'd need a
# better separation between UI and processing
class Runner:
    def __init__(self, pitches):
        self.width = 1400
        self.height = 700
        self.background = self.pitches_to_images(pitches, True)

        self.sample_rate = 44100  # Sample rate in Hz
        self.window_size = 2048  # Window size for STFT
        self.raw_audio_buffer = SlidingBuffer(self.window_size, 1, self.window_size * 255)
        self.notes_buffer = SlidingBuffer(self.width, len(SINGABLE_NOTE_FREQUENCIES), self.width * 4)

    def pitches_to_images(self, pitches, spread_octaves: bool):
        # up = higher note, that requires a flip
        pitches = np.flip(pitches, axis=1)

        # Smooth out the value along the time axis
        for _ in range(10):
            pitches = 0.6 * pitches + 0.4 * self.shift_with_padding(pitches, 1, 0)

        # Set a threshold for minimal values
        # pitches[pitches < 5] = 0

        if spread_octaves:
            # Split out the result over octaves (with lower weight)
            # (makes it easier to sing the same not at a different octave)
            accumulated = np.zeros_like(pitches)
            for i in range(int(pitches.shape[1] / 12)):
                accumulated += np.roll(pitches, i * 12, axis=1)
            pitches = 0.8 * pitches + 0.2 * accumulated

        # Upscale to match the window size
        pitches = np.repeat(pitches, int(self.height / pitches.shape[1]), axis=1)
        pitches = np.repeat(pitches, int(self.width / pitches.shape[0]), axis=0)

        return pygame.surfarray.make_surface(pitches)

    @staticmethod
    def shift_with_padding(array, n, axis):
        if axis == 0:
            return np.pad(array, ((n, 0), (0, 0)), mode="constant")[:-n, :]
        if axis == 1:
            return np.pad(array, ((0, 0), (n, 0)), mode="constant")[:, :-n]

    def run(self):
        pygame.init()
        pygame.display.set_caption("karaoke helper.")
        window_surface = pygame.display.set_mode((self.width, self.height))

        def callback(indata, frames, time, status):
            self.raw_audio_buffer.add(indata)
            s = np.abs(
                librosa.stft(self.raw_audio_buffer.get()[:, 0], n_fft=self.window_size)
            )
            pitches = spectrogram_to_pitches(s)
            pitches = pitches.mean(axis=0)
            self.notes_buffer.add(pitches[None, :])

        # Start the audio stream
        with sd.InputStream(callback=callback, channels=1, samplerate=self.sample_rate):
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return

                self.background = self.pitches_to_images(self.notes_buffer.get(), False)
                window_surface.blit(self.background, (0, 0))
                pygame.display.update()
