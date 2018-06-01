import sys, pygame, time, numpy, copy, random
import pygame.gfxdraw as gfx
from ShipParams import *
from Assets import *
import Classes
import Funcs
import Menus
#from Menus import *

def listen_acceleration(player, keys):

    if keys[pygame.K_UP]:

        player.accelerate(player.ACCELERATION)
        #x.speed[1] += -0.25
        Funcs.FX_engine_mark(player)

    #if keys[pygame.K_UP]:
    #    control_keys[0] = True
    #else:
    #    control_keys[0] = False

def listen_reverse(player, keys):

    if keys[pygame.K_DOWN]:

        player.accelerate(-player.DEACCELERATION)
            #x.speed[1] += 0.25

def listen_right(player, keys):

    if keys[pygame.K_RIGHT]:

        player.rotate(player.ROTATION)

        for x in player.turrets:
            x.rotate(player.ROTATION)
            Funcs.orbit_rotate(player, x, -player.ROTATION,
                               x.distance, x.orbit_ang)
            #x.speed[0] += 0.25
        for x in player.shields:
            x.rotate(player.ROTATION)

        for x in player.player_hull_group:
            Funcs.orbit_rotate(player, x, -player.ROTATION,
                               x.distance, x.orbit_ang)

def listen_left(player, keys):


    if keys[pygame.K_LEFT]:
        player.rotate(-player.ROTATION)
           #x.speed[0] += -0.25
        for x in player.turrets:
            x.rotate(-player.ROTATION)
            Funcs.orbit_rotate(player, x, player.ROTATION,
                               x.distance, x.orbit_ang)

        for x in player.shields:
            x.rotate(-player.ROTATION)

        for x in player.player_hull_group:
            Funcs.orbit_rotate(player, x, player.ROTATION,
                               x.distance, x.orbit_ang)

def listen_shot(player, keys):

    if keys[pygame.K_SPACE]:

        player.fire()

def listen_shot_missile(player, keys):

    if keys[pygame.K_x] and player.locks[2] == False:
        player.locks[2] = True
        x = Classes.Missile(0, player.rect.centerx, player.rect.centery)    #d_ang is for eveyry new frame (mul by 30)
        x.look_dir = player.look_dir
        x.speed = copy.deepcopy(player.speed)

def listen_shield(player, keys):

    if  keys[pygame.K_c] and player.locks[3] == False:

        Funcs.shields(player)
        #special_lock = True
    else:
        for x in player.shields:
            x.down()
            player.shields.remove(x)


ABILITIES = [[listen_shield, listen_shot,
            listen_left, listen_right,
            listen_acceleration, listen_reverse],
            [listen_shield, listen_shot,
            listen_left, listen_right,
            listen_acceleration, listen_reverse, listen_shot_missile],
            [listen_shield, listen_shot,
            listen_left, listen_right,
            listen_acceleration, listen_reverse, listen_shot_missile]]
