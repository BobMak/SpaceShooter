import sys
import time
import numpy
import copy
import random
import pygame
import pygame.gfxdraw as gfx
from Menus import main_menu, player_set


pygame.init()

try:
    s = open('C:/vova/scores.txt', 'r')
    s.close()
except:
    s = open('C:/vova/scores.txt', 'w')
    s.write('1')
    s.close()


# main_menu()
player_set()
