"""
Modular ships!
integrity vs utility? Complexity, chaos and emergence vs fun?
Add whatever module you find or manufacture to your (or someone else's?) ship.
"""
import random as r
import numpy as np
import pygame as pg
from Ships import Modules as M
from Core import Utils, Classes


# Ships can be controlled by a player. Ships are composed of modules
# that are placed on a skeleton. Skeletons are bases of sh ip.
# Skeleton is generated around base modules: thrusters and energy generator.
# All other modules are put on top. Skeletons may be extended to accommodate
# new modules.
class Ship(Classes.Object):
    """A controllable ship. Behaviour and abilities are defined by the modules that it consists of"""
    def __init__(self, coords, size=1, seed=None):
        Classes.Object.__init__(self, x=coords[0], y=coords[1])
        # All modules on the ship
        self.modules = []
        self.skeleton_a = []  # Primary mount points: [(x, y), ...]
        self.skeleton_b = []  # Secondary mount points
        # Map of keys to controlled modules
        self.mass         = 0
        self.energy       = 0
        self.energyCap    = 0
        self.energyGen    = 0
        self.integrity    = 0
        self.integrityCap = 0
        self.storage      = 0
        self.propulsion   = 0
        self.maxSpeed     = 0
        self.tasks = {}  # eg. go to x, shoot at y, do z
        self.controls = {
            pg.K_w: self.handleW,
            pg.K_s: self.handleS,
            pg.K_d: self.handleD,
            pg.K_a: self.handleA
        }
        self.dAng = 0

    def updateSystem(self):
        """ When computing the action of a system composed of many modules one
         needs to calculate how all the components influence given behaviour.
         If we have a model that successfully predicts the state of such system,
         we can avoid costly computation.
         In game such systems may be ships or other arrays of modules that can
         act in different ways"""
        for m in self.modules:
            m.rect.centerx = self.rect.centerx + m.placement[0]
            m.rect.centery = self.rect.centery + m.placement[1]
            m.speed = self.speed
            m.  ang = self.ang
        assert self.mass > 0, "Ship's mass can't be zero"
        self.dAng = 1
        self.dSpeed = self.propulsion
        self.maxSpeed = max([m.max_speed for m in self.modules if isinstance(m, M.Propulsion)])

    def spendEnergy(self, energy):
        self.energy += (max(0, energy))

    def damage(self, hp):
        self.integrity += (max(0, hp))

    def handleRightCilck(self, x, y):
        goal = pg.Rect(x, y, 1, 1)
        self.arrived = 0
        self.tasks['moveTo'] = (self.moveTo, goal)

    def handleW(self):
        self.accelerate(self.dSpeed, 0)
        speed = np.sqrt(self.speed[0]**2 + self.speed[1]**2)
        if speed > self.maxSpeed:
            ang = np.arctan(self.speed[1]/self.speed[0])
            self.accelerate(self.dSpeed, ang+180)

    def handleS(self):
        self.accelerate(self.dSpeed, 180)

    def handleD(self):
        self.accelerate(self.dSpeed, 90)

    def handleA(self):
        self.accelerate(self.dSpeed, -90)

    def handleRotate(self, right=1):
        self.rotate(self.dAng * right)

    def moveTo(self, goal):
        dist = self.get_distance(goal)
        speed = max(np.sqrt(self.speed[0] ** 2 + self.speed[1] ** 2), 0.01)
        # Do not stop until close and slowed down
        if dist > 20 or speed>0.01:
            # Face the goal and accelerate if have time to rotate and slow down
            ang_goal = self.get_aim_dir(goal)
            ang = Utils.angle_diff(self.ang, ang_goal)
            # Rotate toward a goal
            if abs(ang) > 0:
                if abs(ang) > self.dAng:
                    self.rotate(np.sign(ang) * self.dAng)
                    ang += -np.sign(ang) * self.dAng
                else:
                    self.rotate(ang)
                    ang = 0
            if abs(ang) <= 1 and speed < self.maxSpeed:
                self.accelerate(self.dSpeed, self.ang)
            return False

        # Success
        else:
            return True

    def rotate(self, deg):
        super().rotate(deg)
        for m in self.modules:
            m.rotate(deg)

    def update(self):
        Classes.Object.update(self)
        _finished = []
        for _type, _func in self.tasks.items():
            # Finish the task if it reports success
            if _func[0](_func[1]):
                _finished.append(_type)
        for _type in _finished:
            self.tasks.pop(_type)


class ShipFactory:
    def generate_specific(self, size, tech, shape) -> Ship:
        raise NotImplementedError()

    @staticmethod
    def generate_test():
        ship = Ship((1, 1))  # Start in the middle of the screen
        M.Propulsion(1, 0.1, 1, max_speed=3).assignShip(ship).place(0, 50)
        M.Hull(5).assignShip(ship).place(0, 10)
        M.Capacitor(1, 5).assignShip(ship).place(40, 0)
        M.Generator(1, 1).assignShip(ship).place(-40, 0)
        M.Weapon(1, 1).assignShip(ship).place(0, -40)
        ship.updateSystem()
        return ship

    def generate_r_l(self):
        # Ships are built based on r vectors defining their role.
        # These roles, along with constrains such as max tech level and cost, should be used to generate a ship.
        # Role is a vector consisting of following dimensions: attack, defence, support-attack, support-defence
        # There might be modules that may be used for different roles.

        # Fleets may contain different roles to compensate for weaknesses and strengthen powers of individual ships.
        # 1 drone  2 Gunship 3 Corvette 4 frigate 5 Destroyer 6 cruiser 7 Battleship 8 flagship 9 carrier 10 giant
        size = r.randint(0, 10)
        max_tech = r.randint(0, 10)  # max module tech tier
        # what part of modules are around max tech tier. The mean of all modules' tech level bell curve is max_tech*cost
        cost = r.random()  # [0, 1)
        # attack:defence, support-attack:support-defence
        role = [r.random(), r.random()]
        mu = cost * max_tech
        sigma = 2
        # Centered around special ability? TODO: How to combine several abilities and AI for their operation?
        # Ship skeleton and other modules might be placed to support that ability
        centered = r.random()
        # generate skeleton
        sim = r.choice([True, False])  # symmetrical or asymmetrical
        size = size//2 if sim else size
        radius = int(np.sqrt((max((size + r.randint(-4,4)), 1)) * 100))
        radius_diff = r.uniform(-4,4)
        sk_tor = self.generate_skeleton_torus
        sk_rec = self.generate_skeleton_rect
        sk_tri = self.generate_skeleton_triangle
        skeleton = r.choice([sk_tor, sk_rec, sk_tri])(size, radius, radius_diff, sim)
        # self.generate_module(type, size, tech, distribution)

    def generate_skeleton_torus(self, size, radius, radius_var, symmetry=True):
        points = []
        for point in range(size):
            angle = r.random() * 2 * np.pi
            x = np.cos(angle) * radius + r.uniform(-radius_var, radius_var)
            y = np.sin(angle) * radius + r.uniform(-radius_var, radius_var)
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
            x = r.uniform(-radius, radius) + r.uniform(-radius_var, radius_var)
            y = radius - (2*np.absolute(x))     + r.uniform(-radius_var, radius_var)
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
            x = r.uniform(-radius, radius) + r.uniform(-radius_var, radius_var)
            y = radius - (2*np.absolute(x))     + r.uniform(-radius_var, radius_var)
            points.append((x, y))
            if symmetry:
                points.append((-x, y))
        return points

