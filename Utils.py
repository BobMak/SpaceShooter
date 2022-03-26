import hashlib
import json
import math

import numpy as np
import pygame

import State


def get_dist(dx, dy):
    return np.sqrt(dx**2 + dy**2)


def angle_diff(a1, a2):
    """angle_1 - angle_2 with regards to used angle system"""
    a = a1 - a2
    if abs(a) > 180:
        return np.sign(a)*360 - a
    else:
        return a


def get_angle(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.atan2(y2 - y1, x2 - x1) * 180 / math.pi


def blur(obj, velocity):
    '''blur effect along the velocity direction'''
    rect = obj.rotated_image.get_rect()
    img = obj.rotated_image_alpha

    for x in range(int(velocity)//3):
        rect.centerx = obj.rect.centerx + obj.v[0] // (x + 3)
        rect.centery = obj.rect.centery + obj.v[1] // (x + 3)
        State.screen.blit(img, rect)
        rect.centerx = obj.rect.centerx - obj.v[0] // (x + 3)
        rect.centery = obj.rect.centery - obj.v[1] // (x + 3)
        State.screen.blit(img, rect)


def orbit_rotate(center, obj, d_ang, dist = 0, ang = -20):
    """orbit_rotate(center, obj, d_ang, dist = 0, ang = -20)
    rotate 'obj' by the orbit of 'center' on range of 'dist'
    from center of 'center' by angle 'ang'. 'obj' has to have angle argument"""
    if ang == -20:

        dx = obj.rect.centerx - center.rect.centerx
        dy = obj.rect.centery - center.rect.centery

        if dx > 0 and dy < 0:
            ang = abs(np.rad2deg(np.arctan(dx/dy)))
        elif dx < 0 and dy < 0:
            ang = abs(np.rad2deg(np.arctan(dy/dx)))
        elif dx > 0 and dy > 0:
            ang = abs(np.rad2deg(np.arctan(dy/dx)))
        elif dx < 0 and dy > 0:
            ang = abs(np.rad2deg(np.arctan(dx/dy)))
        else:
            ang = 90
    else:

        obj.orbit_ang += d_ang

        if obj.orbit_ang > 360:
            obj.orbit_ang += -360
        elif obj.orbit_ang < 0:
            obj.orbit_ang += 360

        ang = obj.orbit_ang

    if dist == 0:
        pass

    obj.rect.centerx = center.rect.centerx + dist*(np.sin(np.deg2rad(ang)))
    obj.rect.centery = center.rect.centery + dist*(np.cos(np.deg2rad(ang)))


def orbit_eliptic(center, obj):
    """
    orbit_eliptic(center, obj)
    obj orbits center on median distance of 'm_dist' with angular velocity d_ang.
    'orbit_coef' shows how many times in one full turn 'obj' reaches
    its perigee or apsis.
    'd_dist' is the differance between apsis/perigee and the median
    """
    obj.distance += obj.d_dist*obj.d_dist_dir

    if obj.distance < obj.min_dist:
        obj.d_dist_dir = 1

    elif obj.distance > obj.max_dist:
        obj.d_dist_dir = -1

    orbit_rotate(center, obj, obj.d_ang, obj.distance, obj.orbit_ang)


def draw_triangle(player, color, dist_to_edg, width):
    bufx1 = (player.rect.centerx
          + dist_to_edg * np.cos(np.deg2rad(player.look_dir - 90)))
    bufx2 = (player.rect.centerx
          + dist_to_edg * np.cos(np.deg2rad(player.look_dir + 120 - 90)))
    bufx3 = (player.rect.centerx
          + dist_to_edg * np.cos(np.deg2rad(player.look_dir - 120 - 90)))
    bufy1 = (player.rect.centery
          + dist_to_edg * np.sin(np.deg2rad(player.look_dir - 90)))
    bufy2 = (player.rect.centery
          + dist_to_edg * np.sin(np.deg2rad(player.look_dir + 120 - 90)))
    bufy3 = (player.rect.centery
          + dist_to_edg * np.sin(np.deg2rad(player.look_dir - 120 - 90)))
    pygame.draw.polygon(State.screen, color,
                        ((bufx1, bufy1), (bufx2, bufy2), (bufx3, bufy3)), width)


def dict_hash(dictionary) -> str:
    """MD5 hash of a dictionary."""
    dhash = hashlib.md5()
    # We need to sort arguments so {'a': 1, 'b': 2} is
    # the same as {'b': 2, 'a': 1}
    encoded = json.dumps(dictionary, sort_keys=True).encode()
    dhash.update(encoded)
    return dhash.hexdigest()
