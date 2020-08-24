"""
Modular ships!
integrity vs utility?
Add whatever module you find or manufacture to your (or someone else's?) ship.
"""
import pyglet as pg
import numpy as np
import copy

from Core import Assets as A, State as St, Classes


class Module(Classes.Object, Classes.Vulnerable):
    """ A basic part of the ship."""
    def __init__(self, image=None, hp=1, mass=1):
        if not image:
            image = pg.resource.image("Ball.png")
        Classes.Object.__init__(self, image=image, x=0, y=0)
        Classes.Vulnerable.__init__(self, hp=hp)
        self.             ship = None
        self.               hp = hp
        self.             mass = mass
        self.connected_modules = []
        self.        placement = (0, 0)  # x, y with respect to ships center
        self.           radius = 0   # distance from ship's center to module
        self.        place_ang = 0   # angle at which the module is placed in radians

    def connect_module(self, module):
        self.connected_modules.append(module)

    # Only after the ship was assigned
    def place(self, x, y):
        assert self.ship, "Can't place a module without ship"
        self.placement = (x, y)
        # self.placement_angles =
        _x = self.ship.position[0] + x
        _y = self.ship.position[1] + y
        self.position = [_x, _y]
        self.radius = np.sqrt(self.placement[0]**2 + self.placement[1]**2)
        self.place_ang = np.arctan2(x, y)
        return self

    def assignShip(self, ship):
        self.ship = ship
        ship.mass += self.mass
        ship.modules.append(self)
        return self

    def set_rotation(self, deg):
        # Rotate the sprite around its center
        super().set_rotation(deg - self.place_ang)
        # Rotate the sprite around module carrier's center
        # deg = abs(deg)
        new_deg = self.place_ang - deg * np.pi / 180
        rot_x = np.sin(new_deg) * self.radius
        rot_y = np.cos(new_deg) * self.radius
        self.position[0] = self.ship.position[0] - rot_x  # - self.placement[0]
        self.position[1] = self.ship.position[1] - rot_y  # - self.placement[1] 
        # self.position = (_x, _y)
        self.rect[0] = int(self.position[0])
        self.rect[1] = int(self.position[1])


class Hull(Module):
    """ Nothing but integrity and cns between other modules"""
    def __init__(self, hp):
        image = pg.resource.image("Ball.png")
        Module.__init__(self, hp=hp, image=image)


class Storage(Module):
    """ Can contain other modules """
    def __init__(self, capacity: int, integrity: int):
        image = pg.resource.image("Ball.png")
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
        :param distance: dist from center of the block
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
        image = pg.resource.image("Ball.png")
        Module.__init__(self, hp=hp, mass=mass, image=image)

        self.      range = range
        self.restriction = restriction
        self.   distance = distance

        if type[0] == 'bl':
            self.shot = self._shot_projectile
            self.prj_speed = type[2]
            self.reload = type[3] / St.FPS
            self.passive_energy_drain = type[3] * type[4] / St.FPS
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
        predict_pos = Classes.Object(pg.resource.image("blanc.png"), 0, 0)
        predict_pos.rect = copy.copy(locked.rect)
        length = np.sqrt((self.rect.x - locked.rect.x)**2
               + (self.rect.y - self.target.rect.y)**2)
        try:
            if (self.prj_speed*np.cos(np.deg2rad(self.ang))) != -99:
                predict_pos.rect[0] += (round(self.target.speed[0] * length/self.prj_speed)
                    * (1/self.prj_speed + 1))
        except:
            pass
        try:
            if (self.prj_speed*np.sin(np.deg2rad(self.ang))) != -99:
                predict_pos.rect[1] += (round(self.target.speed[1] * length/self.prj_speed)
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
            shot = Classes.Projectile(self.bolt, self.rect[0],
                                      self.rect[1], self.range)
            shot.ang = self.ang
            shot.rect[0] = (self.rect[0]
                            - skipped_len * np.cos(np.deg2rad(shot.ang + 90)))
            shot.rect[1] = (self.rect[1]
                            - skipped_len * np.sin(np.deg2rad(shot.ang + 90)))
            shot.speed = [self.speed * np.cos(np.deg2rad(self.ang - 90)),
                          self.speed * np.sin(np.deg2rad(self.ang - 90))]
            shot.rotate(0)
            return shot

    def _shot_projectile(self):
        raise NotImplementedError("Weapon Projectile")


class Network(Module):
    """ Interconnection between modules within the ship
    Ex: Power networks in bigger ships, physical communication networks within the ship
    """
    def __init__(self, hp):
        _len = 15
        image = pg.resource.image("Ball.png")
        mass = 1
        Module.__init__(self, hp=hp, mass=mass, image=image)


class Propulsion(Module):
    """ Might be divided on several modules """
    def __init__(self, hp, propulsion, consump=0.1, mass=1, max_speed=1):
        image = pg.resource.image("Ball.png")
        Module.__init__(self, hp=hp, mass=mass, image=image)
        self.max_speed = max_speed
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
        image = pg.resource.image("Ball.png")
        mass = 1
        Module.__init__(self, hp=hp, mass=mass, image=image)
        self.energyGen = energyGen

    def assignShip(self, ship):
        Module.assignShip(self, ship)
        ship.energyGen += self.energyGen
        return self


class Capacitor(Module):
    def __init__(self,hp, energyCapacity):
        image = pg.resource.image("Ball.png")
        mass = 1
        Module.__init__(self, hp=hp, mass=mass, image=image)
        self.energyCap = energyCapacity
        self.part = None


class Shield(Module):
    """ :param hitBoxArr: list of all rects that shield covers """
    def __init__(self, hp, shieldCapacity):
        image = pg.resource.image("Ball.png")
        mass = 1
        Module.__init__(self, hp=hp, image=image, mass=mass)
        self.shieldCapacity = shieldCapacity
        self.hitBoxList = []

