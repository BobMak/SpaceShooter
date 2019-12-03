"""
This file contains game state and all relevant variables
"""
import pickle
import pygame as pg

SIZE = WIDTH, HEIGHT = (1200, 900)
WHITE= (255, 255, 255)

INPUTS_PER_SECOND = 30
FRAMES_PER_SECOND = 60
LOGIC_PER_SECOND = 240

# Game parameters
# Key locks
t = (True, True, True, True)
FPS = 30
screen = pg.display.set_mode((SIZE[0], SIZE[1]))
graphics = None
graphics_thread = None
# Game is paused or not
paused = False
# Player object. Does it belong here?
player = None
# Collection of all current objects
all_objects = []
verse = None
# Window instance
window = None


