import random
import threading
import time

import numpy as np
import pygame

import Scripts
import State
from Agressor import Agressor
from Assets import bad_thing
from Player import Player


def thrusters():
    time.sleep(2)
    print("Testing linear force")
    for x in range(20):
        State.pl.apply_force_linear(2, 0)

    for x in range(20):
        State.pl.apply_force_linear(2, np.pi)

    print("Testing angular force")
    for x in range(20):
        State.pl.rotate(-1)

    for x in range(20):
        State.pl.rotate(1)


if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((1200, 720))
    State.pl = Player.ship_assign("tick", 1)
    threading.Thread(target=thrusters).start()
    Scripts.main_loop()

    pygame.quit()

