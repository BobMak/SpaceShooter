"""
This file contains game state and all relevant variables
"""
import os
import pickle
import pygame as pg
import Classes as C
import Map as M

WHITE= (255, 255, 255)

INPUTS_PER_SECOND = 30
FRAMES_PER_SECOND = 60
LOGIC_PER_SECOND = 240

# Game parameters
# Key locks
t = (True, True, True, True)
FPS = 30
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


def init():
    for obj, cls in zip(["player", "verse", "window"], [C.Player, M.Verse, M.Window]):
        try:
            with open('../data/{}.pkl'.format(obj), 'rb') as f:
                globals()[obj] = pickle.load(f)
        except:
            globals()[obj] = cls()


def save():
    for obj, cls in zip(["player", "verse", "window"], [C.Player, M.Verse, M.Window]):
        try:
            if 'data' in os.listdir('../data'):
                with open('../data/{}.pkl'.format(obj), 'rb') as f:
                    globals()[obj] = pickle.load(f)
            else:
                os.mkdir("../data", 777)
                raise Exception()
        except:
            globals()[obj] = cls()
