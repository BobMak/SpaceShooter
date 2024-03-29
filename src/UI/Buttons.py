import pickle
import random
import traceback

import pygame as pg

from Core.Assets import *
from Core import Scripts, State
from Entities.Player import Player
from Ships.ShipGen import Generator


class Button(pygame.sprite.Sprite):

    text = '---'
    font = 0

    def __init__(self, rect, state):
        pygame.sprite.Sprite.__init__(self)
        self.state = state
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

    def __init__(self, rect, state):
        super().__init__(rect, state)
        self.text = 'Continue'

    def action(self):
        self.state.t = (True, True, True, True)
        self.state.state = "game"


class B_Start_Over(Button):
    '2'
    def __init__(self, rect, state):
        super().__init__(rect, state)
        self.text = 'Start Over'

    def action(self):
        # global t
        self.state.t = (True, True, True, True)

        for object in self.state.player_group:
            object.v = [0, 0]
            object.kill()
        for object in self.state.movable:
            object.kill()
        for object in self.state.interface:
            object.kill()

        self.state.save['level'] = 0
        self.state.config = 0

        Scripts.spawn_wave(self.state)
        self.state.state = 'new_game'


class B_New_Game(Button):
    '3'
    def __init__(self, rect, state):
        super().__init__(rect, state)
        self.text = 'New Game'

    def action(self):
        self.state.config = 0
        self.state.state = 'new_game'


class B_Stats(Button):
    '4'
    def __init__(self, rect, state):
        super().__init__(rect, state)
        with open('save.pkl', 'rb') as f:
            pickle.dump(self.state.save, f, pickle.HIGHEST_PROTOCOL)

    def action(self):
        pass


class B_Exit(Button):
    '5'
    def __init__(self, rect, state):
        super().__init__(rect, state)
        self.text = 'Exit'

    def action(self):
        self.state.state = "quit"


class B_Ship_Highlihgts(Button):
    '6'
    def __init__(self, rect, ship_number, state):

        super().__init__(rect, state)
        self.ship_number = ship_number
        self.text = State.ship_types[ship_number]['controls_text']

        self.main_image = State.ship_types[ship_number]['image']
        ship_rect = self.main_image.get_rect()
        self.ship_img_pos = (rect[2]//2 - ship_rect.width//2,
                             rect[3]//2 - ship_rect.height//2)

        self.image = pygame.transform.scale(menu_button,
                                            [self.rect.width, self.rect.height])

        self.image.blit(self.main_image, (self.ship_img_pos[0],
                                          self.ship_img_pos[1]))

    def action(self):
        self.state.picked_ship = self.ship_number
        if self.ship_number == 'generated':
            try:
                g = Generator()
                img = g.generateShipSurf()
                # save img as generated.png
                State.ship_types[self.ship_number]['image'] = img
                pygame.image.save(img, os.path.join('assets', 'ships', 'generated.png'))
                abilities = ['left', 'right', 'up', 'down']
                for x in ['shoot', 'shield', 'velocity', 'health','missile']:
                    if random.choice([True, False]):
                        abilities.append(x)

                State.ship_types['generated']['rotation_rate'] = max(1.0, random.random() * 5)
                State.ship_types['generated']['acceleration'] = max(0.1, random.random())
                State.ship_types['generated']['deacceleration'] = max(0.1, random.random())
                State.ship_types['generated']['env_deacceleration'] = max(
                    min(State.ship_types['generated']['acceleration'] - 0.05, random.random()),
                    0.01)
                State.ship_types['generated']['acceleration_tank'] = max(1.0, random.random() * 5)
                State.ship_types['generated']['hull'] = max(1.0, random.random() * 10)
                State.ship_types['generated']['shields'] = 3
                State.ship_types['generated']['mass'] = 1
                State.ship_types['generated']['missile'] = random.choice(['light_missile', 'heavy_missile', 'medium_missile'])
                State.ship_types['generated']['bolt'] = random.choice(['light_bolt', 'heavy_bolt', 'medium_bolt', 'big_bolt'])
                State.ship_types['generated']['abilities'] = abilities
            except Exception as e:
                print(f'error generating ship: {e}\n{traceback.format_exc()}')

        self.main_image = State.ship_types[self.ship_number]['image']
        ship_rect = self.main_image.get_rect()
        self.ship_img_pos = (self.rect[2] // 2 - ship_rect.width // 2,
                             self.rect[3] // 2 - ship_rect.height // 2)
        self.image = pygame.transform.scale(menu_button_selected,
                                            [self.rect.width, self.rect.height])
        self.image.blit(self.main_image, (self.ship_img_pos[0],
                                          self.ship_img_pos[1]))

    def select(self):
        self.image = pygame.transform.scale(menu_button_selected,
                                            [self.rect.width, self.rect.height])

        self.main_image = State.ship_types[self.ship_number]['image']
        ship_rect = self.main_image.get_rect()
        self.ship_img_pos = (self.rect[2] // 2 - ship_rect.width // 2,
                             self.rect[3] // 2 - ship_rect.height // 2)

        self.image.blit(self.main_image, (self.ship_img_pos[0],
                                          self.ship_img_pos[1]))

    def deselect(self):
        self.image = pygame.transform.scale(menu_button,
                                            [self.rect.width, self.rect.height])
        self.image.blit(self.main_image, (self.ship_img_pos[0],
                                          self.ship_img_pos[1]))
