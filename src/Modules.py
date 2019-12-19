"""
Modular ships!
integrity vs utility?
Add whatever module you find or manufacture to your (or someone else's?) ship.
"""
import random as r
import sys
import pygame as pg
import numpy as np
import copy

import Assets as A, State as St
import Classes


class Module(Classes.Object, Classes.Vulnerable):
    """ A basic part of the ship."""
    def __init__(self, image=None, hp=1, mass=1):
        if not image:
            image = pg.Surface((30*1.5, 30*1.5), flags=pg.SRCALPHA)
            pg.gfxdraw.box(image, (0, 0, 30, 30), (160, 160, 160, 200))
        Classes.Object.__init__(self, image=image, x=0, y=0)
        Classes.Vulnerable.__init__(self, hp=hp)
        self.             ship = None
        self.               hp = hp
        self.             mass = mass
        self.connected_modules = []
        self.        placement = (0, 0)  # x, y with respect to ships center
        self.           radius = 0  # distance from ship center to module
        self.        place_ang = 0  # angle at which the module is placed

    def passive(self):
        """ Passive turn. To be run every logic update"""
        raise NotImplementedError("Module Passive Ability")

    def active(self):
        """ Passive turn. To be run every logic update"""
        raise NotImplementedError("Module Active Ability")

    def connect_module(self, module):
        self.connected_modules.append(module)

    # Only after the ship was assigned
    def place(self, x, y):
        assert self.ship, "No ship"
        self.placement = (x, y)
        _x = self.ship.position[0] + x
        _y = self.ship.position[1] + y
        self.position = (_x, _y)
        self.radius = np.sqrt(self.placement[0]**2 + self.placement[1]**2)
        self.place_ang = np.arcsin(y / self.radius)
        return self

    def assignShip(self, ship):
        self.ship = ship
        ship.mass += self.mass
        ship.modules.append(self)
        return self

    def rotate(self, deg):
        self.place_ang += deg*np.pi/180
        rot_x = np.cos(self.place_ang) * self.radius
        rot_y = np.sin(self.place_ang) * self.radius
        self.placement = (rot_x, rot_y)
        _x = self.ship.position[0] + rot_x
        _y = self.ship.position[1] + rot_y
        self.position = (_x, _y)
        print(self.placement)
        super().rotate(deg)

    def draw(self):
        print("--fakeDrawing")


class Hull(Module):
    """ Nothing but integrity and connections between other modules"""
    def __init__(self, hp):
        image = pg.Surface((50*1.5, 50*1.5), flags=pg.SRCALPHA)
        pg.gfxdraw.box(image, (0, 0, 50, 50), (90, 190, 90, 200))
        Module.__init__(self, hp=hp, image=image)


class Storage(Module):
    """ Can connect other modules"""
    def __init__(self, capacity: int, integrity: int):
        image = pg.Surface((40*1.5, 40*1.5), flags=pg.SRCALPHA)
        pg.gfxdraw.box(image, (0, 0, 40, 40), (110, 110, 110, 200))
        Module.__init__(self, hp=integrity, image=image)
        self.capacity = capacity

    def assignShip(self, ship):
        Module.assignShip(self, ship)
        ship.capacity += self.capacity


class Weapon(Module):
    """ Anything that can generate projectiles, damage fields, May rotate"""
    def __init__(self, hp, mass,
            distance=20,
            restriction=None,
            type=('bl', 1, 2, 2, 3),
            range=50,
            energy_drain=1):
        """
        :param carrier: Ship
        :param image:
        :param distance: dist from center of the block
        :param look_dir: direction of weapon with respect to carrier
        :param x: x with respect to the center of carrier
        :param y: y with respect to the center of carrier
        :param width: rect property
        :param height: rect property
        :param restriction: max rotation angle of the weapon
        :param type: 'bl' - ballistic, will use pre-aim func to shot; 'ls' - laser
            ballistic type: ('bl', bolt number, bolt speed, load speed in seconds, energy to load)
            laser type: ('ls', laser number)
        :param range: weapon's range
        :param energy_drain: how much energy is used per shot
        """
        self.      aim = None
        self.  aim_dir = None
        self.orbit_ang = None
        self.  distance = 0
        self.    d_dist = 0
        self.d_dist_dir = -1  # 1 or -1 -- is object getting closer or further
        image = pg.Surface((20*1.5, 20*1.5), flags=pg.SRCALPHA)
        pg.gfxdraw.box(image, (0, 0, 20, 20), (190, 30, 30, 200))
        Module.__init__(self, hp=hp, mass=mass, image=image)

        self.      range = range
        self.restriction = restriction
        self.   distance = distance

        if type[0] == 'bl':
            self.shot = self._shot_projectile
            self.prj_speed = type[2]
            self.reload = type[3] / St.FPS
            self.passive_energy_drain = type[3] * type[4] / St.FPS
        elif type[0] == 'ls':
            self.shot = self._shot_laser
        self.target = None
        self.bolt = [1]
        self.active_energy_drain = energy_drain

    def aim(self, aim, precision=5):
        """ Rotate weapon towards current target (aim)
        :param aim: object"""
        x = (self.ang - self.get_aim_dir(aim))
        if x < precision and x > -precision:
            return True
        elif abs(x) > 180:
            self.rotate(5 * np.sign(x))
        else:
            self.rotate(-5 * np.sign(x))

    def _ballistic_get_predict_pos(self, locked):
        """ Calculate a position where to aim
        :param locked: Object
        :return:
        """
        predict_pos = Classes.Object(A.blanc, 0, 0)
        predict_pos.rect = copy.copy(locked.rect)
        length = np.sqrt((self.rect.x - locked.rect.x)**2
               + (self.rect.y - self.target.rect.y)**2)
        try:
            if (self.prj_speed*np.cos(np.deg2rad(self.ang))) != -99:
                predict_pos.rect.centerx += (round(self.target.speed[0] * length/self.prj_speed)
                    * (1/self.prj_speed + 1))
        except:
            pass
        try:
            if (self.prj_speed*np.sin(np.deg2rad(self.ang))) != -99:
                predict_pos.rect.centery += (round(self.target.speed[1] * length/self.prj_speed)
                    * (1/self.prj_speed + 1))
        except:
            pass

        if self.blocked:
            self.time_count += 1
            if self.time_count > self.timer:
                self.time_count = 0
                self.blocked = False

    def shot(self):
        """Has to be overwritten with specified function"""
        if not self.blocked:
            self.blocked = True
            # TODO Add timer event
            skipped_len = self.rect.height // 2
            shot = Classes.Projectile(self.bolt, self.rect.centerx,
                              self.rect.centery, self.range)
            shot.ang = self.ang
            shot.rect.centerx = (self.rect.centerx
                                 - skipped_len * np.cos(np.deg2rad(shot.ang
                                                                   + 90)))
            shot.rect.centery = (self.rect.centery
                                 - skipped_len * np.sin(np.deg2rad(shot.ang
                                                                   + 90)))
            shot.speed = [self.speed * np.cos(np.deg2rad(self.ang - 90)),
                          self.speed * np.sin(np.deg2rad(self.ang - 90))]
            shot.rotate(0)

    def _shot_projectile(self):
        raise NotImplementedError("Weapon Projectile")

    def _shot_laser(self):
        if self.aim(self.target) and self.target.get_dist() < self.range:
            gl = Classes.FX_Glow(self.rect, 1, 10, 5, (255, 0, 0))
            # self.target


class Network(Module):
    """ Interconnection between modules within the ship
    Ex: Power networks in bigger ships, physical communication networks within the ship
    """
    def __init__(self, hp):
        _len = 15
        image = pg.Surface((_len*1.5, _len*1.5), flags=pg.SRCALPHA)
        pg.gfxdraw.box(image, (0, 0, _len, _len), (120, 160, 200, 200))
        mass = 1
        Module.__init__(self, hp=hp, mass=mass, image=image)


class Propulsion(Module):
    """ Might be divided on several modules """
    def __init__(self, hp, propulsion, consump):
        image = pg.Surface((30*1.5, 30*1.5), flags=pg.SRCALPHA)
        pg.gfxdraw.box(image, (0, 0, 30, 30), (50, 50, 220, 200))
        mass=1
        Module.__init__(self, hp=hp, mass=mass, image=image)
        self.consump = consump
        self.propulsion = propulsion

    def assignShip(self, ship):
        Module.assignShip(self, ship)
        ship.propulsion += self.propulsion
        ship.controls['mouse_right'] = ship.handleRightCilck
        return self


class Generator(Module):
    """ Might be divided on several modules """
    def __init__(self, hp, energyGen):
        image = pg.Surface((40*1.5, 40*1.5), flags=pg.SRCALPHA)
        pg.gfxdraw.box(image, (0, 0, 40, 40), (150, 10, 10, 200))
        mass  = 1
        Module.__init__(self, hp=hp, mass=mass, image=image)
        self.energyGen = energyGen

    def assignShip(self, ship):
        Module.assignShip(self, ship)
        ship.energyGen += self.energyGen
        return self


class Capacitor(Module):
    def __init__(self,hp, energyCapacity):
        image = pg.Surface((50*1.5, 50*1.5), flags=pg.SRCALPHA)
        pg.gfxdraw.box(image, (0, 0, 50, 50), (10, 10, 250, 200))
        mass = 1
        Module.__init__(self, hp=hp, mass=mass, image=image)
        self.energyCap = energyCapacity
        self.part = None


class Shield(Module):
    """
    :param hitBoxArr: list of all rects that shield covers
    """
    def __init__(self, hp, shieldCapacity):
        image = pg.Surface((20*1.5, 20*1.5), flags=pg.SRCALPHA)
        pg.gfxdraw.box(image, (0, 0, 20, 20), (90, 90, 250, 200))
        mass = 1
        Module.__init__(self, hp=hp, image=image, mass=mass)
        self.shieldCapacity = shieldCapacity
        self.hitBoxList = []
