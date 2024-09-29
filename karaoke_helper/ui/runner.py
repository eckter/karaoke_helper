import pygame


class Runner:
    def __init__(self, background):
        self.background = background

    def run(self):
        pygame.init()

        pygame.display.set_caption('karaoke helper.')
        window_surface = pygame.display.set_mode((800, 600))

        is_running = True
        while is_running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

            window_surface.blit(self.background, (0, 0))
            pygame.display.update()
