import copy
from Assets import *
import Funcs
from Mechanics import Animation
from Missile import Missile


def listen_acceleration(player, keys):
    if keys[pygame.K_UP]:
        player.accelerate(player.acceleration)
        Animation.FX_engine_mark(player)


def listen_reverse(player, keys):
    if keys[pygame.K_DOWN]:
        player.accelerate(-player.deacceleration)


def listen_right(player, keys):
    if keys[pygame.K_RIGHT]:
        player.rotate(player.rotation_rate)

        for x in player.turrets:
            x.rotate(player.rotation_rate)
            Funcs.orbit_rotate(player, x, -player.rotation_rate,
                               x.distance, x.orbit_ang)

        for x in player.shields:
            x.rotate(player.rotation_rate)

        for x in player.player_hull_group:
            Funcs.orbit_rotate(player, x, -player.rotation_rate,
                               x.distance, x.orbit_ang)


def listen_left(player, keys):
    if keys[pygame.K_LEFT]:
        player.rotate(-player.rotation_rate)
        for x in player.turrets:
            x.rotate(-player.rotation_rate)
            Funcs.orbit_rotate(player, x, player.rotation_rate,
                               x.distance, x.orbit_ang)

        for x in player.shields:
            x.rotate(-player.rotation_rate)

        for x in player.player_hull_group:
            Funcs.orbit_rotate(player, x, player.rotation_rate,
                               x.distance, x.orbit_ang)


def listen_shot(player, keys):
    if keys[pygame.K_SPACE]:
        player.fire()


def listen_shot_missile(player, keys):
    if keys[pygame.K_x] and player.locks[2] == False:
        player.locks[2] = True
        if player.missiles > 0:
            player.missiles -= 1
            Missile.shot(player, player.look_dir, player.missile)
            # x.speed = copy.deepcopy(player.speed)


def listen_shield(player, keys):
    if keys[pygame.K_c] and player.locks[3] == False:
        Funcs.shields(player)
    else:
        for x in player.shields:
            x.down()
            player.shields.remove(x)


controls = {
    "left": listen_left,
    "right": listen_right,
    "up": listen_acceleration,
    "down": listen_reverse,
    "shoot": listen_shot,
    "missile": listen_shot_missile,
    "shield": listen_shield
}
