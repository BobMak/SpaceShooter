"""
This file contains game state and all relevant variables
"""
import pygame as pg


# CONSTANTS

map_size = m_width, m_size = 3000, 3000
SIZE = WIDTH, HEIGHT = 720, 576
BLACK = 0, 0, 0
WHITE = 255, 255, 255
GREEN = 0, 255, 0
MAX_BALL_SPEED = 10

#####################      Ships       ####################

#              rotation rate    deacceleration        hull   shields type(mass)
#                      acceleration    env. deacceleration
SHIP_CONSTANTS = [[1.6666, 0.4166, 0.0333,   0.0083,    5,      2,      1],
                  [  1.25,  0.025, 0.0125,    0.005,   15,      5,      2],
                  [   2.5, 0.0625,   0.05,   0.0125,  7.5,    2.5,      1],
                  [   1.2,   0.03,   0.01,     0.01,    2,      2,      1],
                  []]


picked_ship = 2
EXPL = 9
start_lives = 2

INPUTS_PER_SECOND = 30
FRAMES_PER_SECOND = 60
LOGIC_PER_SECOND = 240

# prj_cooldown = [500, 300, 1000]     # milliseconds
prj_cooldown = [10, 20, 30, 20, 30, 80]     # frames
prj_speeds = [20, 10, 15, 8]
prj_distances = [20, 150, 60]
bolt_damage = [6, 40, 14, 90, 100, 300]
n_bolts = 3

msl_max_speeds = [5]
msl_d_angs = [5, 10, 3]
msl_d_speeds = [0.25, 0.5, 0.8]
msl_distances = [500, 300, 100]
msl_hit_ranges = [50, 20, 100]

spec_cooldown = [30, 60, 120]

complex_rects = [
    [[20,20,20,-180], [20,20,20,0], [18,18,38,-180], [18,18,38,0]],
    [[20,20,0,0],[10,10,25,-180],[15,15,15,-180],[15,15,15,70],[15,15,15,-70],[15,15,20,0]],
    [[20,20,0,0]]
]

asteroid_hps = [2, 3, 4, 5]
asteroid_noclip_timers = [45, 30, 20, 10]
asteroid_velocity_deviations = [1, 2, 3, 4]
asteroid_densities = [(1,2), (2,2), (1,3), (2,3)]

SHIP_HP = [40, 23, 10]

SHIPS_TEXTS = ['space - shoot, c - shield',
               'space - shoot, c - shield, x - missile',
               'space - shoot, c - shield, x - missile',
               'space - shoot, c - shield']

# Standard save for a player. Should be replaced by a save if such is present in save.pkl
save = {
    'score': 0,
    'level': 0,
    'ship': {
        'picked_ship': 0,
        'abilities': [],
        'control': 100,
        'evolutions': 0,
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

screen = pg.display.set_mode((SIZE[0], SIZE[1]))
graphics_thread = None

# Game is paused or not
paused = False

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
