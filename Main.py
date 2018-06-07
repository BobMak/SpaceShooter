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
# fix frizzing on enemy spawn

# removed extra go() command on spawn of Agressor
# improved starting menu - text only on the right
# removed explosions FX from asteroid crash
# added Track_FX instead
# modified ship texts

pygame.init()

try:
    s = open('scores.txt', 'r')
    s.close()
except:
    s = open('scores.txt', 'w')
    s.write('1')
    s.close()

player_set()
