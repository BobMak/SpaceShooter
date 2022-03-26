from Mechanics import *


class Zone(pygame.sprite.Sprite, Vulnerable):

    def __init__(self, x, y, radius, hp, time):

        pygame.sprite.Sprite.__init__(self)
        Vulnerable.__init__(self, hp)
        self.radius = radius
        self.time_count = 0
        self.timer = time
        self.rect = pygame.Rect(x, y, 1, 1)
        # to calculate repulsion force when calculating collisions
        self.m = hp
        self.v = (0, 0)
