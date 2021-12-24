"""
This file contains game state and all relevant variables
"""
import os

import pygame
import pygame as pg
from Assets import SIZE

#####################      Ships       ####################

ship_types = {
    'tick': {
        'image': pygame.image.load(os.path.join('assets', 'ships', 'tick.png')),
        'rotation_rate': 1.6666,
        'deacceleration': 0.4166,
        'acceleration': 0.1333,
        'env_deacceleration': 0.1,
        'hull': 5,
        'shields': 2,
        'mass': 1,
        'bolt': 'light_bolt',
        'missile': 'light_missile',
        'missiles': 5,
        'acceleration_tank': 20.0,
        'acceleration_burn_rate': 0.01,
        'acceleration_reserve_regeneration': 0.008,
        'controls': ['left', 'right', 'up', 'down', 'shoot', 'shield'],
        'controls_text': 'shoot - space\nleft - a\nright - d\nup - w\ndown - s\nshield - c',
        'hit_box':[[20,20,0,0]]
    },
    'hippo': {
        'image': pygame.image.load(os.path.join('assets', 'ships', 'hippo.png')),
        'rotation_rate': 1.25,
        'deacceleration': 0.025,
        'acceleration': 0.125,
        'env_deacceleration': 0.005,
        'hull': 15,
        'shields': 5,
        'mass': 2,
        'bolt': 'heavy_bolt',
        'missile': 'heavy_missile',
        'missiles': 5,
        'acceleration_tank': 8.0,
        'acceleration_burn_rate': 0.6,
        'acceleration_reserve_regeneration': 0.5,
        'controls': ['left', 'right', 'up', 'down', 'shoot', 'shield', 'missile'],
        'controls_text': 'shoot - space\nleft - a\nright - d\nup - w\ndown - s\nshield - c\nmissile - x',
        'hit_box':[[20,20,20,-180], [20,20,20,0], [18,18,38,-180], [18,18,38,0]]
    },
    'wolf': {
        'image': pygame.image.load(os.path.join('assets', 'ships', 'wolf.png')),
        'rotation_rate': 2.5,
        'deacceleration': 0.0625,
        'acceleration': 0.55,
        'env_deacceleration': 0.0125,
        'hull': 7.5,
        'shields': 2.5,
        'mass': 1,
        'bolt': 'light_bolt',
        'missile': 'light_missile',
        'missiles': 10,
        'acceleration_tank': 16.0,
        'acceleration_burn_rate': 0.6,
        'acceleration_reserve_regeneration': 0.5,
        'controls': ['left', 'right', 'up', 'down', 'shoot', 'shield', 'missile'],
        'controls_text': 'shoot - space\nleft - a\nright - d\nup - w\ndown - s\nshield - c\nmissile - x',
        'hit_box': [[20,20,0,0],[10,10,25,-180],[15,15,15,-180],[15,15,15,70],[15,15,15,-70],[15,15,20,0]]
    },
    'wolf2': {
        'image': pygame.image.load(os.path.join('assets', 'ships', 'wolf2.png')),
        'rotation_rate': 2.5,
        'deacceleration': 0.0625,
        'acceleration': 0.1,
        'env_deacceleration': 0.0125,
        'hull': 12.5,
        'shields': 10.5,
        'mass': 1,
        'bolt': 'medium_bolt',
        'missile': 'medium_missile',
        'missiles': 10,
        'acceleration_tank': 20.0,
        'acceleration_burn_rate': 0.6,
        'acceleration_reserve_regeneration': 0.5,
        'controls': ['left', 'right', 'up', 'down', 'shoot', 'shield', 'missile'],
        'controls_text': 'shoot - space\nleft - a\nright - d\nup - w\ndown - s\nshield - c\nmissile - x',
        'hit_box': [[20,20,0,0],[10,10,25,-180],[15,15,15,-180],[15,15,15,70],[15,15,15,-70],[15,15,20,0]]
    },
    'generated': {
        'image': pygame.image.load(os.path.join('assets', '1live.png')),
        'rotation_rate': 2.5,
        'deacceleration': 0.0625,
        'acceleration': 0.5,
        'env_deacceleration': 0.0125,
        'hull': 7.5,
        'shields': 2.5,
        'mass': 1,
        'bolt': 'light_bolt',
        'missile': 'light_missile',
        'missiles': 10,
        'acceleration_tank': 16.0,
        'acceleration_burn_rate': 0.6,
        'acceleration_reserve_regeneration': 0.5,
        'controls': ['left', 'right', 'up', 'down', 'shoot', 'shield', 'missile'],
        'controls_text': '',
        'hit_box': [[32,32,0,0]],
    }
}


picked_ship = 'tick'
EXPL = 9
start_lives = 2

INPUTS_PER_SECOND = 30
FRAMES_PER_SECOND = 60
LOGIC_PER_SECOND = 240


projectile_types = {
    'light_bolt': {
        'damage': 6,
        'speed': 20,
        'distance': 20,
        'cooldown': 10,
        'image': pygame.image.load(os.path.join('assets', 'projectiles','light_bolt.png')),
    },
    'big_bolt': {
        'damage': 40,
        'speed': 10,
        'distance': 150,
        'cooldown': 20,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'big_bolt.png')),

    },
    'medium_bolt': {
        'damage': 14,
        'speed': 15,
        'distance': 60,
        'cooldown': 30,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'medium_bolt.png')),
    },
    'heavy_bolt': {
        'damage': 90,
        'speed': 8,
        'distance': 100,
        'cooldown': 100,
        'image': pygame.image.load(os.path.join('assets', 'projectiles',  'heavy_bolt.png')),
    },
}

missile_types = {
    'light_missile': {
        'damage': 10,
        'speed': 5,
        'rotation_speed': 10,
        'distance': 500,
        'hit_range': 20,
        'cooldown': 50,
        'acceleration': 0.2,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'light_missile.png')),
    },
    'medium_missile': {
        'damage': 25,
        'speed': 3,
        'rotation_speed': 3,
        'distance': 500,
        'hit_range': 50,
        'cooldown': 80,
        'acceleration': 0.15,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'medium_missile.png')),
    },
    'heavy_missile': {
        'damage': 100,
        'speed': 2,
        'rotation_speed': 2,
        'distance': 1000,
        'hit_range': 100,
        'cooldown': 150,
        'acceleration': 0.15,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'heavy_missile.png')),
    },
}

spec_cooldown = [30, 60, 120]

asteroid_hps = [2, 3, 4, 5]
asteroid_noclip_timers = [45, 30, 20, 10]
asteroid_velocity_deviations = [1, 2, 3, 4]
asteroid_densities = [(1,2), (2,2), (1,3), (2,3)]


# Standard save for a player. Should be replaced by a save if such is present in save.pkl
save = {
    'score': 0,
    'level': 0,
    'ship': {
        'picked_ship': '',
        'abilities': [],
    },
}

# GAME STATE
# Should be accessed through designated getters and setters

# Game parameters

bound_break_vert = False
bound_break_hor = False
t = (True, True, True, True)
score = 0
FPS = 30

# Level parameters:
# Asteroids quantitiy, asteriods level
levels = [[4, 0], [5, 1], [6, 2], [5, 3]]
level = 0
wave_spawning = False
pl = None

screen = pg.display.set_mode((SIZE[0], SIZE[1]))
graphics = None
graphics_thread = None

# Game is paused or not
state = 'game_started'
# 'paused'
# 'game_over'
# 'game_won'
# 'player_selection'
# 'game_started'
# 'game_playing'
# 'exit'


# Collection of all current objects
all_objects = []

movable = pg.sprite.Group()

asteroids = pg.sprite.Group()
noclip_asteroids = pg.sprite.Group()
outside_asteroids = pg.sprite.Group()
projectiles = pg.sprite.Group()
mob_goal = pg.sprite.Group()

missiles = pg.sprite.Group()
hit_waves = pg.sprite.Group()
time_dependent = pg.sprite.Group()

player_group = pg.sprite.Group()
mob_group = pg.sprite.Group()
script_mob_group = pg.sprite.Group()

glow = pg.sprite.Group()
effects = pg.sprite.Group()
interface = pg.sprite.Group()
pickupables = pg.sprite.Group()