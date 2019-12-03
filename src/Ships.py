"""
Modular ships!
integrity vs utility? Complexity, chaos and emergence vs fun?
Add whatever module you find or manufacture to your (or someone else's?) ship.
"""
import random
import numpy as np
import copy

import Assets as A, State as St, Modules as M
import Classes


class Ship(C.Object, C.Moving):
    """A controllable ship. Behaviour and abilities are defined by the modules that it consists of"""
    def __init__(self, modules: [M.Module], coords):
        C.Object.__init__(self, St.window.current_sector,
                          x=coords[0], y=coords[1])
        C.Moving.__init__(self, St.window.current_sector)
        # All modules on the ship
        self.modules = modules
        # Map of keys to controlled modules
        self.        mass = 0
        self.      energy = 0
        self.   energyCap = 0
        self.   energyGen = 0
        self.   integrity = 0
        self.integrityCap = 0
        self.     storage = 0
        self.  propulsion = 0
        for x in self.modules:
            x.assignShip(self)
        self.dAng = self.dAcc = self.propulsion / (self.mass**2)

    def addModule(self, module):
        """ This only happens when module gets attached to a ship """
        self.modules.append(module)
        module.assignShip(self)

    def update_system(self):
        """ When computing the action of a system composed of many modules one
         needs to calculate how all the components influence given behaviour.
         If we have a model that successfully predicts the state of such system,
         we can avoid costly computation.
         In game such systems may be ships or other arrays of modules that can
         act in different ways"""

    def spendEnergy(self, energy):
        self.energy += (max(0, energy))

    def damage(self, hp):
        self.integrity += (max(0, hp))

    def move_to(self, goal):
        """ Given a location and modules, what are most optimal sets of actions
        to reach it? Eg. most energy-efficient vs quickest"""
        dist = self.get_distance(goal)
        if dist > 50:
            speed_mod = np.sqrt(self.speed[0] ** 2 + self.speed[1] ** 2)
            # If speed is small, turn in the direction of goal,
            # otherwise, in the direction allowing greater speed vecror change
            if speed_mod < 1:
                t = self.ang - abs(self.get_aim_dir(goal))
            else:
                ang = np.arctan(self.speed[0] / self.speed[1])
                # Direction of motion
                spe = C.Object(sector=St.window.current_sector,
                    x=int(self.rect.centerx + 30*np.sin(ang)*np.sign(self.speed[1])),
                    y=int(self.rect.centery + 30*np.cos(ang)*np.sign(self.speed[1]))
                    )
                true_ang = self.get_aim_dir(goal) - self.get_aim_dir(spe)
                spe.kill()
                if true_ang < -180 or true_ang > 180:
                    true_ang = -360 * np.sign(true_ang) + true_ang

                if true_ang < -90 or true_ang > 90:
                    t = self.get_aim_dir(goal)
                else:
                    t = self.get_aim_dir(goal) + true_ang
                # true_ang = self.get_aim_dir(self.goal) - true_ang
                t = self.ang - t
                if t > 360 or t < -360:
                    t += -360 * np.sign(t)
            if abs(t) > self.dAng:
                if t < -180 or t > 180:
                    t = -t
                self.rotate(-np.sign(t) * self.dAng)
            if abs(t) < 90:
                self.accelerate(self.dAcc, self.ang)
            else:
                self.accelerate(self.dAcc, self.ang)

    def draw(self):
        for m in self.modules:
            m.draw(self.rect)


class ShipGenerator:
    def generate_specific(self, size, tech, shape) -> Ship:
        raise NotImplementedError()

    @staticmethod
    def generate_test():
        p = M.Propulsion(1, 5, 1).place(0, 50)
        h = M.Hull(5).place(0, 10)
        e = M.Capacitor(1, 5).place(20, 0)
        g = M.Generator(1, 1).place(-20, 0)
        w = M.Weapon(1, 1).place(0, -10)
        ship = Ship([p, h, e, g, w], (50, 50))
        ship.update_system()
        return ship

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
        # attack:defence, support-attack:support-defence
        role = [random.random(), random.random()]
        mu = cost * max_tech
        sigma = 2
        # Centered around special ability? TODO: How to combine several abilities and AI for their operation?
        # Ship skeleton and other modules might be placed to support that ability
        centered = random.random()
        # generate skeleton
        sim = random.choice([True, False])  # symmetrical or asymmetrical
        size = size//2 if sim else size
        radius = int(np.sqrt((max((size + random.randint(-4,4)), 1)) * 100))
        radius_diff = random.uniform(-4,4)
        sk_tor = self.generate_skeleton_torus
        sk_rec = self.generate_skeleton_rect
        sk_tri = self.generate_skeleton_triangle
        skeleton = random.choice([sk_tor, sk_rec, sk_tri])(size, radius, radius_diff, sim)
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
