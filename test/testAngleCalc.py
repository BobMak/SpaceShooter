import pygame
from Core import Scripts, State
from Core.Mechanics import GObject

if __name__ == '__main__':
    pygame.init()
    display = pygame.display.set_mode((50, 50))
    state = State.State()
    for q1 in range(-1, 2, 1):
        for q2 in range(-1, 2, 1):
            go1 = GObject.make_blank_obj(state, 0,0)
            go2 = GObject.make_blank_obj(state, q1,q2)
            print('\n------testing quadrant:', q1, q2, '------')

            go1.look_dir = 0
            print('aim dir', go1.get_angle_to(go2))
            print('relative angle', go1.get_relative_angle(go2))
