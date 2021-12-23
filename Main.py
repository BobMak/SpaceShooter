"""
Initial script
"""
import pygame
import pickle
from Scripts import player_set
import State


pygame.init()

try:
    with open('save.pkl', 'rb') as f:
        State.save = pickle.load(f)
except:
    print('No save file found.')

player_set()