import sys
import time
import numpy
import copy
import pygame
import pygame.gfxdraw as gfx
from Menus import main_menu, player_set

"""
Initial script
"""

# removed extra go() command on spawn of Agressor
# improved starting menu - text only on the right
# removed explosions FX from asteroid crash
# added Track_FX instead
# modified ship texts

# TODO: Create hierarchy of classes for menus.
# TODO: Fix initial speed of asteroids to be a float
# TODO: Create one input thread that is always active and add multi-threading input handling for different game states
# TODO: Fix frizzing on enemy spawn

pygame.init()

try:
    s = open('scores.txt', 'r')
    s.close()
except:
    s = open('scores.txt', 'w')
    s.write('1')
    s.close()

player_set()
