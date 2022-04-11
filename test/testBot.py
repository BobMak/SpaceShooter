import random

import pygame

from Core import Scripts, State
from Entities.Chaser import Chaser
from Core.Assets import bad_thing
from Entities.Player import Player


if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((1200, 720))
    state = State.State()
    state.pl = Player.ship_assign("tick", 1, state)
    ag = Chaser(bad_thing, random.randint(0, 1200), random.randint(0, 1200), state=state)
    Scripts.main_loop(state)

    pygame.quit()

