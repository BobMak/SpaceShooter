"""
Initial script
"""
import pygame
import pickle
from Scripts import player_set
import State

# fix frizzing on enemy spawn

# removed extra go() command on spawn of Agressor
# improved starting menu - text only on the right
# removed explosions FX from asteroid crash
# added Track_FX instead
# modified ship texts

# TODO: Store objects that exceed visibility
# TODO: scalable event architecture. Add laziness

pygame.init()

try:
    with open('save.pkl', 'rb') as f:
        State.save = pickle.load(f)
except:
    print('No save file found.')

player_set()