import pygame as pg

from Core import Assets as A


class Button(pg.sprite.Sprite):
    text = '---'
    font = 0

    def __init__(self, rect):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(A.menu_button, [rect[2], rect[3]])
        self.rect = self.image.get_rect()
        self.rect.left = rect[0]
        self.rect.top = rect[1]
        self.rect.width = rect[2]
        self.rect.height = rect[3]
        self.font = pg.font.Font(pg.font.get_default_font(), 23)

    def select(self):
        self.image = pg.transform.scale(A.menu_button_selected,
                                            [self.rect.width, self.rect.height])

    def deselect(self):
        self.image = pg.transform.scale(A.menu_button,
                                            [self.rect.width, self.rect.height])

