import numpy as np
import pygame


# Code architecture is very bare-bone and quite clunky there,
# this is just an early prototype. Eventually we'd need a
# better separation between UI and processing
class Runner:
    def __init__(self, pitches):
        self.width = 1400
        self.height = 700
        self.background = self.pitches_to_images(pitches)

    def pitches_to_images(self, pitches):
        # Smooth out the value along the time axis
        for _ in range(10):
            pitches = 0.6 * pitches + 0.4 * self.shift_with_padding(pitches, 1, 0)

        # Set a threshold for minimal values
        pitches[pitches < 5] = 0

        # Split out the result over octaves (with lower weight)
        accumulated = np.zeros_like(pitches)
        for i in range(int(pitches.shape[1] / 12)):
            accumulated += np.roll(pitches, i * 12, axis=1)
        pitches = 0.9 * pitches + 0.1 * accumulated

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

        is_running = True
        while is_running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

            window_surface.blit(self.background, (0, 0))
            pygame.display.update()
