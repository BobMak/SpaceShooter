import time

import pygame

from Missile import Missile
from Mechanics import Animation


if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((350, 350))
    hit_range = 100

    for _ in range(5):
        expAnimation = Missile.generateExplosionAnimation(hit_range, hit_range)
        for i in range(0, len(expAnimation)):
            display.blit(expAnimation[i], (0, 0))
            pygame.display.update()
            pygame.time.delay(50)
    pygame.quit()

