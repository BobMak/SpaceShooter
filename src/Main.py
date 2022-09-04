"""
Initial script
"""
import pygame
import pickle
from Core.Scripts import main_loop
from Core import State


if __name__ == '__main__':
    pygame.init()
    state = State.State()
    try:
        with open('../save.pkl', 'rb') as f:
            state.save = pickle.load(f)
    except:
        print('No save file found.')

    main_loop(state)