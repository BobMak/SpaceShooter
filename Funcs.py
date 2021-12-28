import numpy as np
import pygame

import Assets
import State
from Shield import Shield


def get_dist(dx, dy):
    return np.sqrt(dx**2 + dy**2)


def angle_diff(a1, a2):
    """angle_1 - angle_2 with regards to used angle system"""
    a = a1 - a2
    if abs(a) > 180:
        return np.sign(a)*360 - a
    else:
        return a


def shields(source):
    if len(source.shields) == 0:
        shld_obj = Shield(Assets.shield, source.rect.width+10,
                                  source.rect.height+10, source.rect.left,
                                  source.rect.top, source, 1)

        shld_obj.rotate(source.look_dir)
        source.sh_add(shld_obj)
        State.effects.add(shld_obj)


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
    obj orbits center on median distance of 'm_dist' with angular speed d_ang.
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


def bound_collision(obj):
    global bound_break_vert
    global bound_break_gor

    if obj.rect.left < 0 or obj.rect.right > Assets.WIDTH:

        #if bound_break_gor == False:
        obj.speed[0] = -obj.speed[0]
        #   bound_break_gor = True
    else:
        bound_break_gor = False
    if obj.rect.top < 0 or obj.rect.bottom > Assets.HEIGHT:
       # control_keys[0:4] = False, False, False, False
        #if bound_break_vert == False:
        obj.speed[1] = -obj.speed[1]
        #bound_break_vert = True
    else:
        bound_break_vert = False
    return bound_break_gor, bound_break_vert
