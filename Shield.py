import State
from Mechanics import Animation

import pygame.gfxdraw as gfx


class Shield(Animation):

    source = 0
    def __init__(self, images_arr, width, height, x, y, source, type = 0):
        super().__init__(images_arr, width, height, x, y, type)
        self.source = source
        self.look_dir = 0
        self.rotate(0)
        self.speed = source.speed
        self.type = type
        self.HP = source.shield_hp

        self.rect.width = width
        self.rect.height = height
        self.rect.centerx = source.rect.centerx
        self.rect.centery = source.rect.centery

        source.shields.add(self)

    def update(self):
        self.rect.centerx = self.source.rect.centerx
        self.rect.centery = self.source.rect.centery

    def down(self):
        self.type = 3
        self.source.locks[3] = True
        self.kill()

    def damage(self, dmg):
        global shield_lock
        self.HP += -max(0, dmg)

        if self.HP < 0:
            self.down()
