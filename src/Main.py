"""
Initial script
"""
import pygame
import pickle
from Core.Scripts import player_set
from Core import State


if __name__ == '__main__':
    pygame.init()
    state = State.State()
    try:
        with open('../save.pkl', 'rb') as f:
            state.save = pickle.load(f)
    except:
        print('No save file found.')

    player_set(state)