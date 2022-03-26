from Assets import *
from Mechanics import Animation
from Missile import Missile
from Shield import Shield


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
    elif not keys[pygame.K_LEFT]:
        player.rotation_rate = 0


def listen_left(player, keys):
    if keys[pygame.K_LEFT]:
        player.rotate(-player.rotation_rate)
    elif not keys[pygame.K_RIGHT]:
        player.rotation_rate = 0


def listen_shot(player, keys):
    if keys[pygame.K_SPACE]:
        player.fire()


def listen_shot_missile(player, keys):
    if keys[pygame.K_x] and player.locks[2] == False:
        player.locks[2] = True
        if player.missiles > 0:
            player.missiles -= 1
            Missile.shot(player, player.look_dir, player.missile)


def listen_shield(player, keys):
    if keys[pygame.K_c] and player.locks[3] == False:
        Shield.shields(player)
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
