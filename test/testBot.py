import random
import time

import pygame

import Scripts
import State
from Agressor import Agressor
from Assets import bad_thing
from Player import Player


if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((1400, 1400))
    State.pl = Player.ship_assign("tick", 1)
    ag = Agressor(bad_thing, random.randint(0, 1400), random.randint(0, 1400))
    ag.remove(State.player_group)
    ag.rush()
    Scripts.main_loop()

    pygame.quit()
