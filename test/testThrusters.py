import threading
import time

import numpy as np
import pygame

from Core import Scripts, State
from Entities.Player import Player


def thrusters(state):
    time.sleep(2)
    print("Testing linear force")
    for x in range(20):
        state.pl.apply_force_linear(2, 0)

    for x in range(20):
        state.pl.apply_force_linear(2, np.pi)

    print("Testing angular force")
    for x in range(20):
        state.pl.rotate(-1)

    for x in range(20):
        state.pl.rotate(1)


if __name__ == '__main__':
    pygame.init()
    state = State.State()
    display = pygame.display.set_mode((1200, 720))
    State.pl = Player.ship_assign("tick", 1, state)
    threading.Thread(target=thrusters, args=(state,)).start()
    Scripts.main_loop(state)

    pygame.quit()

