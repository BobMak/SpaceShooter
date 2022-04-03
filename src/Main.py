"""
Initial script
"""
import pygame
import pickle
from Core.Scripts import player_set
from Core import State

pygame.init()

try:
    with open('../save.pkl', 'rb') as f:
        State.save = pickle.load(f)
except:
    print('No save file found.')

player_set()