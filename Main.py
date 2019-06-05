"""
Initial script
"""
import pygame
import pickle
from Scripts import player_set
import State

# TODO: Modify event architecture. Scalability+ Add laziness
# TODO: Modify control mechanic
# TODO: Add abilities mechanic
# TODO: Add rpg-sim part
# TODO: Add Map. Store objects that exceed visibility
# TODO: Add Ship generation

pygame.init()

try:
    with open('save.pkl', 'rb') as f:
        State.save = pickle.load(f)
except:
    print('No save file found.')

player_set()