"""
This file contains game state and all relevant variables
"""
import os
import pickle

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
# Collection of all current objects
all_objects = []
verse = None
# Window instance
window = None
# Game state
gamestate = "game"
Gamestates = ("new_player", "game", "pause", "dead", "main_menu")


def getCurrentSector():
    return window.current_sector


def init():
    for obj in ["window", "verse"]:
        try:
            with open('../data/{}.pkl'.format(obj), 'rb') as f:
                globals()[obj] = pickle.load(f)
                print('loaded', obj)
        except:
            if obj=="window":
                globals()["gamestate"] = "new_player"
            print('no {} to load'.format(obj))


def save():
    for obj in ["window", "verse"]:
        try:
            if 'data' in os.listdir('../data'):
                with open('../data/{}.pkl'.format(obj), 'rb') as f:
                    globals()[obj] = pickle.load(f)
            else:
                os.mkdir("../data", 777)
                raise Exception()
        except:
            print('Failed to save', obj)
