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

# GAME STATE
# Should be accessed through designated getters and setters
# Standard save for a player. Should be replaced by a save if such is present in save.pkl
save = {
    'score': 0,
    'level': 0,
    'ship': None,
    'location': (0, 0),
}
# map storing all objects
map = {
    'sec0': None
}


def load_save():
    try:
        with open('save.pkl', 'rb') as f:
            save = pickle.load(f)
        globals()['save'] = save
    except:
        print('No save file found.')


# Game parameters
# Key locks
t = (True, True, True, True)
FPS = 30
screen = pg.display.set_mode((SIZE[0], SIZE[1]))
graphics = None
graphics_thread = None
# Game is paused or not
paused = False
# Collection of all current objects
all_objects = []
# Window instance
window = None


