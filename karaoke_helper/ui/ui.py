import numpy as np
import pygame

from karaoke_helper.helpers.typing import Pitches


class UI:
    def __init__(self, pitches: Pitches):
        pygame.init()
        pygame.display.set_caption("karaoke helper")
        self._width = 1400
        self._height = 700
        self._background = self._pitches_to_images(pitches, True)
        self._window_surface = pygame.display.set_mode((self._width, self._height))
        self._is_running = True

    def render_pitches(self, pitches: Pitches):
        self._background = self._pitches_to_images(pitches, False)
        self._window_surface.blit(self._background, (0, 0))
        pygame.display.update()

    def is_running(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_running = False
        return self._is_running

    def _pitches_to_images(
        self, pitches: Pitches, spread_octaves: bool
    ) -> pygame.Surface:
        # up = higher note, that requires a flip
        pitches = np.flip(pitches, axis=1)

        # Smooth out the value along the time axis
        for _ in range(10):
            pitches = 0.6 * pitches + 0.4 * self._shift_with_padding(pitches, 1)

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
        pitches = np.repeat(pitches, int(self._height / pitches.shape[1]), axis=1)
        pitches = np.repeat(pitches, int(self._width / pitches.shape[0]), axis=0)

        return pygame.surfarray.make_surface(pitches)

    @staticmethod
    def _shift_with_padding(array: np.ndarray, n: int) -> np.ndarray:
        return np.pad(array, ((n, 0), (0, 0)), mode="constant")[:-n, :]
