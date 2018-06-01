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

pygame.init()

try:
    s = open('scores.txt', 'r')
    s.close()
except:
    s = open('scores.txt', 'w')
    s.write('1')
    s.close()

player_set()
