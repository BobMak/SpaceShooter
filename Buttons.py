import pickle
import pygame as pg
import sys

from Assets import *
import State
import Funcs
import Scripts


class Button(pygame.sprite.Sprite):

    text = '---'
    font = 0

    def __init__(self, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(menu_button, [rect[2], rect[3]])
        self.rect = self.image.get_rect()
        self.rect.left = rect[0]
        self.rect.top = rect[1]
        self.rect.width = rect[2]
        self.rect.height = rect[3]
        self.font = pygame.font.Font(pygame.font.get_default_font(), 23)

    def select(self):
        self.image = pygame.transform.scale(menu_button_selected,
                                            [self.rect.width, self.rect.height])

    def deselect(self):
        self.image = pygame.transform.scale(menu_button,
                                            [self.rect.width, self.rect.height])


class B_Continue(Button):
    '1'

    def __init__(self, rect):
        super().__init__(rect)
        self.text = 'Continue'

    def action(self):
        State.t = False


class B_Start_Over(Button):
    '2'
    def __init__(self, rect):
        super().__init__(rect)
        self.text = 'Start Over'

    def action(self):
        global realGuy
        # global t
        State.t = False

        for object in State.player_group:

            object.speed = [0,0]
            object.kill()
        for object in State.movable:
            object.kill()
        for object in State.interface:
            object.kill()

        realGuy = Funcs.ship_assign(State.picked_ship, State.start_lives,
                              player=True)

        State.save['level'] = 0

        Funcs.spawn_wave(realGuy)
        Scripts.main_loop(realGuy)


class B_New_Game(Button):
    '3'
    def __init__(self, rect):
        super().__init__(rect)
        self.text = 'New Game'

    def action(self):
        State.level = 0

        realGuy = Funcs.ship_assign(State.picked_ship, State.start_lives,
                              player=True)

        Scripts.main_loop(realGuy)


class B_Stats(Button):
    '4'
    def __init__(self, rect):
        super().__init__(rect)
        with open('save.pkl', 'rb') as f:
            pickle.dump(State.save, f, pickle.HIGHEST_PROTOCOL)

    def action(self):
        pass


class B_Exit(Button):
    '5'
    def __init__(self, rect):
        super().__init__(rect)
        self.text = 'Exit'

    def action(self):
        State.paused = False
        pg.event.post(pg.event.Event(pg.QUIT, {'QUIT': True}))
        sys.exit()


class B_Ship_Highlihgts(Button):
    '6'
    def __init__(self, rect, ship_number):

        super().__init__(rect)
        self.ship_number = ship_number
        self.text = State.SHIPS_TEXTS[ship_number]

        self.main_image = SHIPS_IMGS[ship_number]
        ship_rect = self.main_image.get_rect()
        self.ship_img_pos = (rect[2]//2 - ship_rect.width//2,
                             rect[3]//2 - ship_rect.height//2)

        self.image = pygame.transform.scale(menu_button,
                                            [self.rect.width, self.rect.height])

        self.image.blit(self.main_image, (self.ship_img_pos[0],
                                          self.ship_img_pos[1]))

    def action(self):

        State.picked_ship = self.ship_number

    def select(self):
        self.image = pygame.transform.scale(menu_button_selected,
                                            [self.rect.width, self.rect.height])

        self.image.blit(self.main_image, (self.ship_img_pos[0],
                                          self.ship_img_pos[1]))

    def deselect(self):
        self.image = pygame.transform.scale(menu_button,
                                            [self.rect.width, self.rect.height])
        self.image.blit(self.main_image, (self.ship_img_pos[0],
                                          self.ship_img_pos[1]))
