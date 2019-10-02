"""
Modular ships!
integrity vs utility?
"""
import random
import numpy as np
import copy
from src import Assets as A, State as S, Classes as C


class Module(C.Object, C.Vulnerable):
    """
    A basic part of the ship.
    """
    def __init__(self, carrier, hp, image, x, y, width, height):
        C.Object.__init__(self, image=image, x=x, y=y, width=width, height=height)
        C.Vulnerable.__init__(self, hp=hp)

        self.carrier = carrier
        self.connected_modules = []


class Hull(Module):
    """
    Nothing but integrity (or storage?) and connections between other modules
    """
    def __init__(self, carrier, inegrity, image, x, y, width, height):
        Module.__init__(self, carrier=carrier, hp=inegrity, image=image, x=x, y=y, width=width, height=height)


class Weapon(Module):
    """
    Anything that can generate projectiles, damage fields,
    May rotate.
    """
    def __init__(self, carrier, hp, image,
                 distance=20, look_dir=0, x=0, y=0,
                 width=20, height=20,
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

        self.aim = None
        self.aim_dir = None
        self.orbit_ang = None

        self.distance = 0
        self.d_dist = 0
        self.d_dist_dir = -1  # 1 or -1 -- is object getting closer or further

        Module.__init__(self, carrier=carrier, hp=hp, image=image, x=x, y=y, width=width, height=height)

        self.range = range
        self.look_dir = carrier.look_dir + look_dir
        self.restriction = restriction
        self.mounted_on = carrier
        self.distance = distance
        self.speed = carrier.speed

        if look_dir == 0:
            self.orbit_ang = carrier.look_dir - 180
        else:
            self.orbit_ang = carrier.look_dir + look_dir

        if type[0] == 'bl':
            self.shot = self._shot_projectile
            self.prj_speed = type[2]
            self.reload = type[3] / S.FPS
            self.passive_energy_drain = type[3] * type[4] / S.FPS
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
        raise NotImplementedError()

    def _shot_projectile(self):
        raise NotImplementedError()

    def _shot_laser(self):
        if self.aim(self.target) and self.target.get_dist() < self.range:
            gl = C.FX_Glow(self.rect, 1, 10, 5, (255, 0, 0))

            # self.target


class Network(Module):
    """
    Interconnection between modules within the ship
    Ex: Power networks in bigger ships, physical communication networks within the ship
    """
    def __init__(self, carrier, hp, image, x, y, width, height):
        Module.__init__(self, carrier=carrier, hp=hp, image=image, x=x, y=y, width=width, height=height)
        raise NotImplementedError()


class Propulsion(Module):
    """
    Might be divided on several modules
    """
    def __init__(self, carrier, hp, image, x, y, width, height):
        Module.__init__(self, carrier=carrier, hp=hp, image=image, x=x, y=y, width=width, height=height)
        raise NotImplementedError()


class Capacitor(Module):
    def __init__(self, carrier, hp, image, x, y, width, height, energyCapacity):
        Module.__init__(self, carrier=carrier, hp=hp, image=image, x=x, y=y, width=width, height=height)
        self.carrier.energy += energyCapacity
        self.energyCap = energyCapacity
        self.part = None
        raise NotImplementedError()

    def setPart(self):
        self.part = self.energyCap / self.carrier.energyCap

    def deactivate(self):
        self.carrier.energyCap += -self.energyCap


class Shield(Module):
    """
    :param hitBoxArr: list of all rects that shield covers
    """
    def __init__(self, carrier, hp, image, x, y, width, height, hitBoxList, shieldCapacity):
        Module.__init__(self, carrier=carrier, hp=hp, image=image, x=x, y=y, width=width, height=height)
        self.shieldCapacity = shieldCapacity
        self.hitBoxList = hitBoxList
        raise NotImplementedError()


class Ship:
    """A controllable ship. Behaviour and abilities are defined by the modules that it consists of"""

    def __init__(self):
        self.modules = []
        self.energyCap = 10
        self.energy = 0

    def spendEnergy(self, energy):
        self.energy += -energy(max(0, energy))

    def generate_random_l(self):
        # Ships are built based on random vectors defining their role.
        # These roles, along with constrains such as max tech level and cost, should be used to generate a ship.
        # Role is a vector consisting of following dimensions: attack, defence, support-attack, support-defence
        # There might be modules that may be used for different roles.

        # Fleets may contain different roles to compensate for weaknesses and strengthen powers of individual ships.

        # 1 drone  2 Gunship 3 Corvette 4 frigate 5 Destroyer 6 cruiser 7 Battleship 8 flagship 9 carrier 10 giant
        size = random.randint(0, 10)
        max_tech = random.randint(0, 10)  # max module tech tier
        # what part of modules are around max tech tier. The mean of all modules' tech level bell curve is max_tech*cost
        cost = random.random()  # [0, 1)

        # attack, defence, support-attack, support-defence
        role = [random.random(), random.random(), random.random(), random.random()]

        mu = cost * max_tech
        sigma = 2

        # Centered around special ability? TODO: How to combine several abilities and AI for their operation?
        # Ship skeleton and other modules might be placed to support that ability
        centered = random.random()
        #
        # generate skeleton
        sim = random.choice([True, False])  # symmetrical or asymmetrical
        size = size//2 if sim else size
        radius = int(np.sqrt((max((size + random.randint(-4,4)), 1)) * 100))
        radius_diff = random.uniform(-4,4)
        sk_tor = self.generate_skeleton_torus(   size, radius, radius_diff, sim)
        sk_rec = self.generate_skeleton_rect(    size, radius, radius_diff, sim)
        sk_tri = self.generate_skeleton_triangle(size, radius, radius_diff, sim)
        skeleton = random.choice([sk_tor, sk_rec, sk_tri])

        # self.generate_module(type, size, tech, distribution)

    def generate_skeleton_torus(self, size, radius, radius_var, symmetry=True):
        points = []
        for point in range(size):
            angle = random.random() * 2 * np.pi
            x = np.cos(angle) * radius + random.uniform(-radius_var, radius_var)
            y = np.sin(angle) * radius + random.uniform(-radius_var, radius_var)
            points.append((x,y))
            if symmetry:
                points.append((-x, y))
        return points

    def generate_skeleton_triangle(self, size, radius, radius_var, symmetry=True):
        points = []
        points.append((0, -radius))
        points.append((-radius, radius))
        points.append((radius, radius))
        for point in range(size-3):
            x = random.uniform(-radius, radius) + random.uniform(-radius_var, radius_var)
            y = radius - (2*np.absolute(x))     + random.uniform(-radius_var, radius_var)
            points.append((x, y))
            if symmetry:
                points.append((-x, y))
        return points

    def generate_skeleton_rect(self, size, radius, radius_var, symmetry=True):
        points = []
        points.append((0, -radius))
        points.append((-radius, radius))
        points.append((radius, radius))
        for point in range(size-3):
            x = random.uniform(-radius, radius) + random.uniform(-radius_var, radius_var)
            y = radius - (2*np.absolute(x))     + random.uniform(-radius_var, radius_var)
            points.append((x, y))
            if symmetry:
                points.append((-x, y))
        return points

    def generate_module(self, type, size, tech, distribution):
        raise NotImplementedError()
