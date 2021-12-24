import time

import pygame

from Mechanics import Animation


if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((350, 350))
    hit_range = 100

    for _ in range(5):
        expAnimation = Animation.generateExplosionAnimation(hit_range, 20)
        for i in range(0, len(expAnimation)):
            display.blit(expAnimation[i], (0, 0))
            pygame.display.update()
            pygame.time.delay(50)
    pygame.quit()

