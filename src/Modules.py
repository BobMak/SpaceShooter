"""
Modular ships!
integrity vs utility?
Add whatever module you find or manufacture to your (or someone else's?) ship.
"""
import random as r
import numpy as np
import copy

from src import Assets as A, State as St, Classes as C, Ships as Sh


class Module(C.Object, C.Vulnerable):
    """A basic part of the ship."""
    def __init__(self, hp, mass, image):
        C.Object.__init__(self, image=image)
        C.Vulnerable.__init__(self, hp=hp)
        self.mass = mass
        self.connected_modules = []
        self.ship = None

    def passive(self):
        """Passive turn. To be run every logic update"""
        raise NotImplementedError("Module Passive Ability")

    def active(self):
        """Passive turn. To be run every logic update"""
        raise NotImplementedError("Module Passive Ability")

    def connect_module(self, module):
        self.connected_modules.append(module)
        if self not in module.connected_modules:
            module.connect_module(self)

    def connect_ship(self, ship):
        self.ship = ship


class Hull(Module):
    """Nothing but integrity and connections between other modules"""
    def __init__(self, hp):
        mass  = 1
        image = None
        Module.__init__(self, hp=hp, mass=mass, image=image)


class Storage(Module):
    """Can connect other modules"""
    def __init__(self, capacity: int, integrity: int):
        # TODO: generate module image
        image = None
        Module.__init__(hp=integrity, image=image)
        self.capacity = capacity


class Weapon(Module):
    """Anything that can generate projectiles, damage fields, May rotate"""
    def __init__(self, hp, mass,
                 distance=20,
                 restriction=None,
                 type=('bl', 1, 2, 2, ),
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
        image = None
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
        """Rotate weapon towards current target (aim)
        :param aim: object"""
        x = (self.look_dir - self.get_aim_dir(aim))
        if x < precision and x > -precision:
            return True
        elif abs(x) > 180:
            self.rotate(5 * np.sign(x))
        else:
            self.rotate(-5 * np.sign(x))

    def _ballistic_get_predict_pos(self, locked):
        """
        Calculate a position where to aim
        :param locked: Object
        :return:
        """
        predict_pos = C.Object(A.blanc, 0, 0)
        predict_pos.rect = copy.copy(locked.rect)
        length = np.sqrt((self.rect.x - locked.rect.x)**2
               + (self.rect.y - self.target.rect.y)**2)
        try:
            if (self.prj_speed*np.cos(np.deg2rad(self.look_dir))) != -99:
                predict_pos.rect.centerx += (round(self.target.speed[0] * length/self.prj_speed)
                    * (1/self.prj_speed + 1))
        except:
            pass
        try:
            if (self.prj_speed*np.sin(np.deg2rad(self.look_dir))) != -99:
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
            shot = C.Projectile(self.bolt, self.rect.centerx,
                              self.rect.centery, self.range)
            shot.look_dir = self.look_dir
            shot.rect.centerx = (self.rect.centerx
                                 - skipped_len * np.cos(np.deg2rad(shot.look_dir
                                                                   + 90)))
            shot.rect.centery = (self.rect.centery
                                 - skipped_len * np.sin(np.deg2rad(shot.look_dir
                                                                   + 90)))
            shot.speed = [self.speed * np.cos(np.deg2rad(self.look_dir - 90)),
                          self.speed * np.sin(np.deg2rad(self.look_dir - 90))]
            shot.rotate(0)

    def _shot_projectile(self):
        raise NotImplementedError("Weapon Projectile")

    def _shot_laser(self):
        if self.aim(self.target) and self.target.get_dist() < self.range:
            gl = C.FX_Glow(self.rect, 1, 10, 5, (255, 0, 0))
            # self.target


class Network(Module):
    """
    Interconnection between modules within the ship
    Ex: Power networks in bigger ships, physical communication networks within the ship
    """
    def __init__(self, hp):
        image = None
        mass = 1
        Module.__init__(self, hp=hp, mass=mass, image=image)


class Propulsion(Module):
    """
    Might be divided on several modules
    """
    def __init__(self, hp):
        image = None
        mass=1
        Module.__init__(self, hp=hp, mass=mass, image=image)
        raise NotImplementedError()


class Capacitor(Module):
    def __init__(self,hp, energyCapacity):
        image = None
        mass = 1
        Module.__init__(self, hp=hp, mass=mass, image=image)
        self.energyCap = energyCapacity
        self.part = None
        raise NotImplementedError()


class Shield(Module):
    """
    :param hitBoxArr: list of all rects that shield covers
    """
    def __init__(self, hp, image, hitBoxList, shieldCapacity):
        mass = 1
        Module.__init__(self, hp=hp, image=image, mass=mass)
        self.shieldCapacity = shieldCapacity
        self.hitBoxList = hitBoxList
        raise NotImplementedError()
