import copy
from Assets import *
import Classes
import Funcs


def listen_acceleration(player, keys):
    if keys[pygame.K_UP]:
        player.accelerate(player.ACCELERATION)
        Funcs.FX_engine_mark(player)


def listen_reverse(player, keys):
    if keys[pygame.K_DOWN]:
        player.accelerate(-player.DEACCELERATION)


def listen_right(player, keys):
    if keys[pygame.K_RIGHT]:
        player.rotate(player.ROTATION)

        for x in player.turrets:
            x.rotate(player.ROTATION)
            Funcs.orbit_rotate(player, x, -player.ROTATION,
                               x.distance, x.orbit_ang)

        for x in player.player_hull_group:
            Funcs.orbit_rotate(player, x, -player.ROTATION,
                               x.distance, x.orbit_ang)


def listen_left(player, keys):

    if keys[pygame.K_LEFT]:
        player.rotate(-player.ROTATION)
        for x in player.turrets:
            x.rotate(-player.ROTATION)
            Funcs.orbit_rotate(player, x, player.ROTATION,
                               x.distance, x.orbit_ang)

        for x in player.player_hull_group:
            Funcs.orbit_rotate(player, x, player.ROTATION,
                               x.distance, x.orbit_ang)


def listen_shot(player, keys):
    if keys[pygame.K_SPACE]:
        player.fire()


def listen_shot_missile(player, keys):
    if keys[pygame.K_x] and player.locks[2] == False:
        player.locks[2] = True
        x = Classes.Missile(0, player.rect.centerx, player.rect.centery)
        x.look_dir = player.look_dir
        x.speed = copy.deepcopy(player.speed)


ABILITIES = [[listen_shot,
            listen_left, listen_right,
            listen_acceleration, listen_reverse],
            [listen_shot,
            listen_left, listen_right,
            listen_acceleration, listen_reverse, listen_shot_missile],
            [listen_shot,
            listen_left, listen_right,
            listen_acceleration, listen_reverse, listen_shot_missile]]
