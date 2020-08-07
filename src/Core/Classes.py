import random, copy
import numpy as np
import pyglet as pg

from Core import State as St
from Core.Assets import *


class Vulnerable:
    """Inherited by all objects that can be damaged"""
    def __init__(self, hp):
        self.hp = hp

    def damage(self, damage):
        self.hp += -max(0, damage)


class Object:
    def __init__(self, sector=None, image=None, x=None, y=None, rect=None):
        """Sprite with an assigned image spawned at point x y.
        :type sector: Sector,
        :type image: image,
        :type x: int
        :type y: int
        :type rect: pg.Rect,
        """
        if sector:
            self.sector = sector
        else:
            self.sector = St.getCurrentSector()
        self.ang           = 0  # float [0,360)
        self.rotated_image = 0
        self.radius        = None
        self.dmg           = None
        self.time_count    = 0
        self.timer         = 0
        self.type          = 0
        self.updates       = []
        if image:
            self.image       = image
            self.image_alpha = copy.copy(image)
            self.rotated_image = image
            self.rotated_image_alpha = image
            self.rect = [x, y, image.width, image.height]
        elif rect:
            self.rect = rect
        elif x and y:
            self.rect = (x, y, 10, 10)
        else:
            raise Exception('Neither Rect nor Position are provided')
        self.radius = self.rect[2]//2
        # Moving properties
        self.speed = [0.0, 0.0]
        self.position = (self.rect[0], self.rect[1])  # can be float to respect <0 speed
        self.updates.append(self.modify_position)
        self.sector.all_objects.append(self)
        self.sector.updateable.append(self)

    def modify_position(self):
        if self.speed[0] or self.speed[1]:
            self.position = (self.position[0]+self.speed[0], self.position[1]+self.speed[1])
            self.rect = (self.position[0]-self.rect[2]//2, self.position[1]-self.rect[3]//2, self.rect[2], self.rect[3])
            ang = np.arctan(self.speed[1]/self.speed[0])
            self.speed[0] += -np.sign(self.speed[0]) * 0.01 * abs(np.cos(ang))
            self.speed[1] += -np.sign(self.speed[1]) * 0.01 * abs(np.sin(ang))

    def accelerate(self, dl, angle):
        self.speed[0] += dl * np.cos(np.deg2rad(angle - 90.0))
        self.speed[1] += dl * np.sin(np.deg2rad(angle - 90.0))

    def rotate(self, dir):
        # Ensure that look_dir is in range [0 - 360)
        if self.ang >= 360:
            self.ang += dir - 360
        elif self.ang < 0:
            self.ang += 360 + dir
        else:
            self.ang += dir
        if self.rotated_image:
            self.image.rotation = self.ang
            self.rotated_image_alpha.rotation = self.ang

    def get_aim_dir(self, rect):
        """Returns the angle specifying direction to 'aim' object"""
        dx = self.rect[0] - rect[0]
        dy = self.rect[1] - rect[1]
        if dx > 0 and dy < 0:
            aim_dir = abs(np.rad2deg(np.arctan(dx/dy)))
        elif dx < 0 and dy < 0:
            aim_dir = abs(np.rad2deg(np.arctan(dy/dx)))
        elif dx > 0 and dy > 0:
            aim_dir = abs(np.rad2deg(np.arctan(dy/dx)))
        elif dx < 0 and dy > 0:
            aim_dir = abs(np.rad2deg(np.arctan(dx/dy)))
        else:
            aim_dir = 0
        if dx < 0 and dy > 0:
            pass
        elif dx < 0 and dy < 0:
            aim_dir += 90
        elif dx > 0 and dy < 0:
            aim_dir += 180
        elif dx > 0 and dy > 0:
            aim_dir += 270

        return aim_dir

    def get_distance(self, rect):
        """returns distance to object x"""
        return np.sqrt((self.rect[0] - rect[0])**2
                       + (self.rect[1] - rect[1])**2)

    def update(self):
        """Execute all pending callbacks for the object every logic tick!"""
        for f in self.updates:
            f()

    def draw(self):
        self.image.blit(self.rect[0] - St.window.base_x,
                        self.rect[1] - St.window.base_y,
                        self.rect[2], self.rect[3])
        
    def __str__(self):
        return "sector: {}, x: {}, y: {}".format(self.sector, self.rect[0], self.rect[1])


class FX(Object):
    def __init__(self, rect, duration, fading=None, color=None, enlarging=None, speed=None, sector=None):
        """
        :param rect: location
        :param duration:
            effect life duration in ticks
        :param fading:
            ((int [1,255)) num points to fade per one update (not per sec) out of 255,
             (int) num of LOGIC ticks before update)
        :param color:
            (r, g, b, a)
        :param enlarging:
            ((int) pixels to enlarge per tick, num of ticks before enlarge update)
        :param speed:
        """
        # Requires rect to already be there
        Object.__init__(self, sector, rect=rect)
        sector.updateable.append(self)
        self.updates = []
        self.duration = duration
        self.duration_count = 0
        if fading:
            self.fading_count = 0
            self.fading_sum = 0
            self.fading = fading[0]
            self.fading_tempo = fading[1]
            self.updates.append(self.fade)
        if color:
            self.color = color
        else:
            self.color = (255, 255, 255, 255)
        if enlarging:
            self.enlarging_count = 0
            self.enlarging_summ = 1
            self.enlarging = enlarging[0]
            self.enlarging_tempo = enlarging[1]
            self.updates.append(self.enlarge)
        if speed:
            self.speed = speed
    def fade(self):
        raise NotImplemented()

    def enlarge(self):
        raise NotImplemented()
    def update(self, *args):
        raise NotImplemented()


class Projectile(Object):
    def __init__(self, thisSector, speedMax, dmg, image, x, y, distance):
        Object.__init__(image, x, y)
        self.speed_max = speedMax
        self.    timer = distance
        self.      dmg = dmg

    def damage(self, obj):
        buff = copy.copy(obj.hp)
        obj.damage(self.hp)
        self.hp += -buff
        if self.hp < 0:
            self.hp = 0


class Missile(Projectile):
    def __init__(self, bolt, x, y, d_ang=0.5, d_speed=0.1, hit_range=20, max_speed=10):
        super().__init__(bolt, x, y, None, 10, 10, 10)
        self.dist_prev = 500
        self.dist = None
        # how often aim-updaing function to run
        self.compute_tempo = 5
        self.compute_count = 0
        self.aim = None
        self.d_ang = d_ang
        self.d_speed = d_speed
        self.hit_range = hit_range
        self.max_speed = max_speed

    def rotate_to_aim(self):
        aim_dir = self.get_aim_dir(self.aim)
        x = (self.ang - aim_dir)
        if abs(x) > 180:
            self.rotate(self.d_ang*np.sign(x))
        else:
            self.rotate(-self.d_ang*np.sign(x))

    def pursue(self):
        r = copy.copy(self.rect)
        self.rotate_to_aim()
        # If missile is close enough to aim but fails to hit it (starts to get
        # further from aim), missile will detonate.
        self.dist = self.get_distance(self.aim)
        if self.dist > self.dist_prev and self.dist < self.hit_range:
            return
        self.dist_prev = self.dist
        a1 = self.speed[0] + self.d_speed*np.cos(np.deg2rad(self.ang - 90))
        if a1 < self.max_speed and a1 > -self.max_speed:
            self.speed[0] = a1
        else:
            self.speed[0] = self.max_speed*np.cos(np.deg2rad(self.ang - 90))
        a2 = self.speed[1] + self.d_speed*np.sin(np.deg2rad(self.ang - 90))
        if a2 < self.max_speed and a2 > -self.max_speed:
            self.speed[1] = a2
        else:
            self.speed[1] = self.max_speed*np.sin(np.deg2rad(self.ang - 90))


