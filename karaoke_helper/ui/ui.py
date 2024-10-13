from typing import List

import numpy as np
import pygame
from pygame import Surface

from karaoke_helper.audio_processing.lyrics_transcription import Transcript
from karaoke_helper.helpers.typing import Pitches


class WordElement:
    def __init__(self, surface: Surface, height: int, time: float):
        self.surface = surface
        self.height = height
        self.time = time


class UI:
    def __init__(self, transcript: Transcript):
        pygame.init()
        pygame.display.set_caption("karaoke helper")
        self._width = 1400
        self._pitches_height = 650
        self._lyrics_height = 100
        self._window_surface = pygame.display.set_mode(
            (self._width, self._pitches_height + self._lyrics_height)
        )
        self._font = pygame.font.SysFont(None, 25)
        self._is_running = True
        self._words = self._init_words(transcript)

    def render(
        self,
        live_pitches: Pitches,
        ref_pitches: Pitches,
        time: float,
        screen_duration: float,
    ):
        self._window_surface.fill((0, 0, 0))
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
            (self._width / 2, self._pitches_height),
        )
        self._render_word(time, screen_duration)
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
        surface = pygame.transform.scale(surface, (width, self._pitches_height))

        return surface

    @staticmethod
    def _shift_with_padding(array: np.ndarray, n: int) -> np.ndarray:
        return np.pad(array, ((n, 0), (0, 0)), mode="constant")[:-n, :]

    def _render_word(self, time: float, screen_duration: float):
        for word in self._words:
            x = (word.time - time) / screen_duration
            x += 0.5
            if x < -0.2 or x > 1:
                continue
            x *= self._width
            text_rect = word.surface.get_rect()
            text_rect.topleft = (x, self._pitches_height + word.height)
            self._window_surface.blit(word.surface, text_rect)

    def _init_words(self, transcript: Transcript) -> List[WordElement]:
        res = []
        height = 0
        for word in transcript.words:
            surface = self._font.render(word.text, True, (255, 255, 255))
            time = (word.time_start + word.time_end) / 2
            word_height = surface.get_rect().height
            if height + word_height > self._lyrics_height or (
                res and res[-1].time + 1 < time
            ):
                height = 0
            res.append(WordElement(surface, height, time))
            height += word_height + 2
        return res
