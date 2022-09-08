"""
This file contains game state and all relevant variables
"""
import os
import pickle
import threading

import pygame
import pygame as pg

from Core import Assets
from Core.Assets import WIDTH, HEIGHT, menu_button

#####################      Ships       ####################
from Entities.Player import Player

ship_types = {
    'tick': {
        'image': pygame.image.load(os.path.join('assets', 'ships', 'tick.png')),
        'rotation_rate': 9.966,
        'deacceleration': 0.4166,
        'acceleration': 0.1333,
        'env_deacceleration': 0.1,
        'hull': 5,
        'shields': 2,
        'mass': 5,
        'bolt': 'light_bolt',
        'missile': 'light_missile',
        'missiles': 5,
        'acceleration_tank': 20.0,
        'acceleration_burn_rate': 0.01,
        'acceleration_reserve_regeneration': 0.008,
        'controls': ['left', 'right', 'up', 'down', 'shoot', 'shield', 'blink'],
        'controls_text': 'shoot - space\nleft - a\nright - d\nup - w\ndown - s\nshield - c\nblink - b',
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
        'mass': 40,
        'bolt': 'big_bolt',
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
        'mass': 18,
        'bolt': 'medium_bolt',
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
        'mass': 15,
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
        'mass': 20,
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


projectile_types = {
    'light_bolt': {
        'damage': 6,
        'velocity': 20,
        'distance': 20,
        'cooldown': 10,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'light_bolt.png')),
        'expl_params': {
            "diameter": 10,
            "n_frames": 10,
            "decay_rgb": (0, 7, 4),
            "start_rgb": (235, 120, 130),
            "spawn_threshold": 190
        },
    },
    'big_bolt': {
        'damage': 40,
        'velocity': 10,
        'distance': 150,
        'cooldown': 20,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'big_bolt.png')),
        'expl_params': {
            "diameter": 25,
            "n_frames": 10,
            "decay_rgb": (0, 10, 1),
            "start_rgb": (90, 200, 130),
            "spawn_threshold": 60
        },

    },
    'medium_bolt': {
        'damage': 14,
        'velocity': 15,
        'distance': 60,
        'cooldown': 30,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'medium_bolt.png')),
        'expl_params': {
            "diameter": 20,
            "n_frames": 15,
            "decay_rgb": (18, 2, 4),
            "start_rgb": (235, 50, 50),
            "spawn_threshold": 200
        },
    },
    'heavy_bolt': {
        'damage': 90,
        'velocity': 8,
        'distance': 100,
        'cooldown': 100,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'heavy_bolt.png')),
        'expl_params': {
            "diameter": 20,
            "n_frames": 15,
            "decay_rgb": (0, 2, 10),
            "start_rgb": (40, 190, 90),
            "spawn_threshold": 10
        },
    },
}

missile_types = {
    'light_missile': {
        'damage': 10,
        'velocity': 3,
        'rotation_velocity': 10,
        'distance': 500,
        'hit_range': 20,
        'cooldown': 50,
        'acceleration': 0.8,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'light_missile.png')),
        'volley': 3,
        'expl_params': {
            "diameter": 30,
            "n_frames": 20
        }
    },
    'medium_missile': {
        'damage': 25,
        'velocity': 2,
        'rotation_velocity': 3,
        'distance': 500,
        'hit_range': 50,
        'cooldown': 80,
        'acceleration': 1,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'medium_missile.png')),
        'volley': 1,
        'expl_params': {
            "diameter": 50,
            "n_frames": 20
        }
    },
    'heavy_missile': {
        'damage': 100,
        'velocity': 1,
        'rotation_velocity': 2,
        'distance': 1000,
        'hit_range': 100,
        'cooldown': 150,
        'acceleration': 0.2,
        'image': pygame.image.load(os.path.join('assets', 'projectiles', 'heavy_missile.png')),
        'volley': 1,
        'expl_params': {
            "diameter": 80,
            "n_frames": 30
        }
    },
}

waves = {
    0: {
        'hps': 2,
        'velocity_deviations': 1,
        'noclip_timers': 45,
        'densities': (1,2),
        'number': 4,
        'init_speed': 1.0,
        'img_n': 0,
    },
    1: {
        'hps': 3,
        'velocity_deviations': 2,
        'noclip_timers': 30,
        'densities': (2,2),
        'number': 5,
        'init_speed': 1.0,
        'img_n': 1,
    },
    2: {
        'hps': 4,
        'velocity_deviations': 3,
        'noclip_timers': 20,
        'densities': (1,3),
        'number': 6,
        'init_speed': 1.0,
        'img_n': 2,
    },
    3: {
        'hps': 5,
        'velocity_deviations': 4,
        'noclip_timers': 10,
        'densities': (2,3),
        'number': 10,
        'init_speed': 1.0,
        'img_n': 3,
    },

}


# GAME STATE
# Should be accessed through designated getters and setters
class State:
    def __init__(self, width=1280, height=720):
        self.cache_dir = os.path.join('cache')
        self.buff_explosions = {}
        self.picked_ship = 'tick'
        self.EXPL = 9
        self.start_lives = 2

        self.FRAMES_PER_SECOND = 60
        self.LOGIC_PER_SECOND = 240

        self.spec_cooldown = [30, 60, 120]
        # Standard save for a player. Should be replaced by a save if such is present in save.pkl
        self.save = {
            'score': 0,
            'level': 0,
            'ship': {
                'picked_ship': '',
                'abilities': [],
            },
        }

        self.clock = pg.time.Clock()

        # Game parameters

        self.t = (True, True, True, True)
        self.score = 0
        self.FPS = 30

        # Level parameters:

        self.level = 0
        self.wave_spawning = False
        self.pl = None

        self.W = width
        self.H = height

        self.screen = pg.display.set_mode((self.W, self.H))
        self.graphics = None
        self.graphics_thread = None
        # Collection of all current objects
        self.all_objects = []

        self.state = 'menu'

        self.movable = pg.sprite.Group()

        self.asteroids = pg.sprite.Group()
        self.noclip_asteroids = pg.sprite.Group()
        self.outside_asteroids = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.mob_goal = pg.sprite.Group()

        self.missiles = pg.sprite.Group()
        self.hit_waves = pg.sprite.Group()
        self.time_dependent = pg.sprite.Group()

        self.player_group = pg.sprite.Group()
        self.mob_group = pg.sprite.Group()
        self.script_mob_group = pg.sprite.Group()

        self.glow = pg.sprite.Group()
        self.effects = pg.sprite.Group()
        self.interface = pg.sprite.Group()
        self.pickupables = pg.sprite.Group()

    def game_over(state):
        state.state = "game_over"
        state.level = 0
        with open('save.pkl', 'wb') as f:
            pickle.dump(state.save, f, pickle.HIGHEST_PROTOCOL)

    def spawn_player(state):
        buff_sp = pg.sprite.Sprite()
        buff_sp.rect = menu_button.get_rect()
        buff_sp.rect.width = 100
        buff_sp.rect.height = 100
        buff_sp.rect.centerx = state.W / 2
        buff_sp.rect.centery = state.H / 2
        if len(pg.sprite.spritecollide(buff_sp, state.asteroids, 0)) == 0:
            state.interface.empty()
            Player.ship_assign(
                state.picked_ship,
                state.pl.lives, state,
                x=buff_sp.rect.centerx,
                y=buff_sp.rect.centery,
            )
        # Do not spawn player if there are State.asteroids around, and wait 100 milliseconds instead
        else:
            threading.Timer(0.5, state.spawn_player).start()

    def reset(self):
        # Standard save for a player. Should be replaced by a save if such is present in save.pkl
        self.save = {
            'score': 0,
            'level': 0,
            'ship': {
                'picked_ship': '',
                'abilities': [],
            },
        }

        self.clock = pg.time.Clock()

        # Game parameters

        self.t = (True, True, True, True)
        self.score = 0
        self.FPS = 30

        # Level parameters:

        self.level = 0
        self.wave_spawning = False
        self.pl = Player.ship_assign(
            self.picked_ship,
            self.start_lives,
            self
        )
        # Game is paused or not
        # 'paused'
        # 'game_over'
        # 'game_won'
        # 'player_selection'
        # 'game_started'
        # 'game_playing'
        # 'exit'
        # reset

        self.screen = pg.display.set_mode((self.W, self.H))
        self.graphics = None
        self.graphics_thread = None
        # Collection of all current objects
        self.all_objects = []

        self.movable = pg.sprite.Group()

        self.asteroids = pg.sprite.Group()
        self.noclip_asteroids = pg.sprite.Group()
        self.outside_asteroids = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.mob_goal = pg.sprite.Group()

        self.missiles = pg.sprite.Group()
        self.hit_waves = pg.sprite.Group()
        self.time_dependent = pg.sprite.Group()

        self.player_group = pg.sprite.Group()
        self.mob_group = pg.sprite.Group()
        self.script_mob_group = pg.sprite.Group()

        self.glow = pg.sprite.Group()
        self.effects = pg.sprite.Group()
        self.interface = pg.sprite.Group()
        self.pickupables = pg.sprite.Group()