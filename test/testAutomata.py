import pygame
from Core import Scripts, State
from Core.Mechanics import Animation


if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((350, 350))
    hit_range = 100
    n_frames = 30
    spawn_points = 190

    for _ in range(5):
        expAnimation = Animation.generateExplosionAnimation(hit_range, n_frames, (13, 0, 2), (255, 0, 130), spawn_points)
        for i in range(0, len(expAnimation)):
            display.blit(expAnimation[i], (0, 0))
            pygame.display.update()
            pygame.time.delay(50)
    pygame.quit()

