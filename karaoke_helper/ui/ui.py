import numpy as np
import pygame

from karaoke_helper.helpers.typing import Pitches


class UI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("karaoke helper")
        self._width = 1400
        self._height = 700
        self._window_surface = pygame.display.set_mode((self._width, self._height))
        self._is_running = True

    def render_pitches(self, live_pitches: Pitches, ref_pitches: Pitches):
        live_pitches_img = self._pitches_to_images(
            live_pitches, False, self._width // 2
        )
        live_pitches_img.set_alpha(200)
        ref_pitches_img = self._pitches_to_images(ref_pitches, True, self._width)
        self._window_surface.blit(ref_pitches_img, (0, 0))
        self._window_surface.blit(live_pitches_img, (0, 0))
        pygame.draw.line(
            self._window_surface,
            (255, 0, 0),
            (self._width / 2, 0),
            (self._width / 2, self._height),
        )
        pygame.display.update()

    def is_running(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._is_running = False
        return self._is_running

    def _pitches_to_images(
        self, pitches: Pitches, spread_octaves: bool, width: int
    ) -> pygame.Surface:
        # up = higher note, that requires a flip
        pitches = np.flip(pitches, axis=1)

        # Smooth out the value along the time axis
        if spread_octaves:
            for _ in range(10):
                pitches = 0.6 * pitches + 0.5 * self._shift_with_padding(pitches, 1)

        # Set a threshold for minimal values
        # pitches[pitches < 5] = 0

        if spread_octaves:
            # Split out the result over octaves (with lower weight)
            # (makes it easier to sing the same not at a different octave)
            accumulated = np.zeros_like(pitches)
            for i in range(int(pitches.shape[1] / 12)):
                accumulated += np.roll(pitches, i * 12, axis=1)
            pitches = 0.9 * pitches + 0.1 * accumulated

        # Upscale to match the window size
        surface = pygame.surfarray.make_surface(pitches)
        surface = pygame.transform.scale(surface, (width, self._height))

        return surface

    @staticmethod
    def _shift_with_padding(array: np.ndarray, n: int) -> np.ndarray:
        return np.pad(array, ((n, 0), (0, 0)), mode="constant")[:-n, :]
