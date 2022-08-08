from Core.Assets import *
from Core.Mechanics import Animation
from Core.Missile import Missile
from Ships.Shield import Shield
from Ships.Jump import Jump


def listen_acceleration(entity, keys):
    if keys[pygame.K_UP]:
        entity.accelerate(entity.acceleration)
        Animation.FX_engine_mark(entity)


def listen_reverse(entity, keys):
    if keys[pygame.K_DOWN]:
        entity.accelerate(-entity.deacceleration)


def listen_right(entity, keys):
    if keys[pygame.K_RIGHT]:
        entity.rotate(1)
    elif not keys[pygame.K_LEFT]:
        entity.rotation_rate = 0


def listen_left(entity, keys):
    if keys[pygame.K_LEFT]:
        entity.rotate(-1)
    elif not keys[pygame.K_RIGHT]:
        entity.rotation_rate = 0


def listen_shot(entity, keys):
    if keys[pygame.K_SPACE]:
        entity.fire()


def listen_shot_missile(entity, keys):
    if keys[pygame.K_x] and entity.locks[2] == False:
        entity.locks[2] = True
        if entity.missiles > 0:
            entity.missiles -= 1
            Missile.shot(entity, entity.look_dir, entity.missile)


def listen_shield(entity, keys):
    if keys[pygame.K_c] and entity.locks[3] == False:
        Shield.shields(entity)
    else:
        for x in entity.shields:
            x.down()
            entity.shields.remove(x)


def listen_blink(entity, keys):
    if keys[pygame.K_b] and entity.locks[3] == False:
        Jump(entity, entity.look_dir, 200.0, state=entity.state)


controls = {
    "left": listen_left,
    "right": listen_right,
    "up": listen_acceleration,
    "down": listen_reverse,
    "shoot": listen_shot,
    "missile": listen_shot_missile,
    "shield": listen_shield,
    "blink": listen_blink
}
