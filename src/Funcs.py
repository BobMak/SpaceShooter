import numpy as np
import random, pygame
import Assets, State, Classes


def get_dist(dx, dy):
    return np.sqrt(dx**2 + dy**2)


def angle_diff(a1, a2):
    """angle_1 - angle_2 with regards to used angle system"""
    a = a1 - a2
    if abs(a) > 180:
        return np.sign(a)*360 - a
    else:
        return a


def draw_rotating(obj):
    rect = obj.rotated_image.get_rect()
    rect.center = (obj.rect.center)
    State.screen.blit(obj.rotated_image, rect)


def blur(obj, speed):
    '''blur effect along the speed direction'''
    rect = obj.rotated_image.get_rect()
    img = obj.rotated_image_alpha

    for x in range(int(speed)//3):
        rect.centerx = obj.rect.centerx + obj.speed[0]//(x+3)
        rect.centery = obj.rect.centery + obj.speed[1]//(x+3)
        State.screen.blit(img, rect)
        rect.centerx = obj.rect.centerx - obj.speed[0]//(x+3)
        rect.centery = obj.rect.centery - obj.speed[1]//(x+3)
        State.screen.blit(img, rect)


def move_movable():
    for object in State.movable:
        # modify position to avoid loss of <1 values when moving
        object.modify_position()


def FX_explosion(x, y, xpl=Assets.expl, radius=(30, 30)):
    obj = Classes.Animation(xpl, radius[0], radius[1], x, y, True, delay=random.randint(0, 2))
    obj.rect.centerx += - 20
    obj.rect.centery += - 20
    State.effects.add(obj)


def FX_engine_mark(source):
    object = Classes.Animation(Assets.engi, 10, 10,
                               source.rect.centerx, source.rect.centery)
    object.look_dir = source.look_dir
    object.rotate(0)
    object.speed = source.speed

    object.rect.centerx = (source.rect.centerx
                        + source.rect.height//2
                          * np.cos(np.deg2rad(object.look_dir+90)))
    object.rect.centery = (source.rect.centery
                        + source.rect.height//2
                          * np.sin(np.deg2rad(object.look_dir+90)))

    State.effects.add(object)
