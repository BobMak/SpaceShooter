"""
Modular ships!
integrity vs utility? Complexity, chaos and emergence vs fun?
Add whatever module you find or manufacture to your (or someone else's?) ship.
"""
import random
import numpy as np
import pygame as pg
import Classes
import Modules as M
import Utils

# Ships can be controlled by a player. Ships are composed of modules
# that are placed on a skeleton. Skeletons are bases of sh ip.
# Skeleton is generated around base modules: thrusters and energy generator.
# All other modules are put on top. Skeletons may be extended to accommodate
# new modules.
class Ship(Classes.Object):
    """A controllable ship. Behaviour and abilities are defined by the modules that it consists of"""
    def __init__(self, modules: [M.Module], coords):
        Classes.Object.__init__(self, x=coords[0], y=coords[1])
        # All modules on the ship
        self. modules = []
        self.skeleton_a = []  # Primary mount points: [(x, y), ...]
        self.skeleton_b = []  # Secondary mount points
        # Map of keys to controlled modules
        self.        mass = 0
        self.      energy = 0
        self.   energyCap = 0
        self.   energyGen = 0
        self.   integrity = 0
        self.integrityCap = 0
        self.     storage = 0
        self.  propulsion = 0
        self.    maxSpeed = 0
        self.       tasks = {}  # eg. go to x, shoot at y, do z
        # dict of keys and functions associated with them. Every module should
        # add their action callback to this dict. E.g propulsion adds
        # pygame right click code with its move_to function
        self.controls = {}
        self.dAng = 0
        if modules:
            for x in modules:
                x.assignShip(self)
            self.dAng = 1
            self.dSpeed = self.propulsion
        # movement buffer
        self._prev_dist = None

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

    # Use propulsion modules to move to the target. Working with one source of
    # propulsion. Accelerate towards goal while there is enough time to stop by
    # with friction or turn and burn.
    def moveTo(self, goal):
        dist = self.get_distance(goal)
        speed = max(np.sqrt(self.speed[0] ** 2 + self.speed[1] ** 2), 0.01)
        # Do not stop until close and slowed down
        if dist > 20 or speed>0.01:
            # Face the goal and accelerate if have time to rotate and slow down
            ang_goal = self.get_aim_dir(goal)
            # If can stop with friction and speed is not maxed out
            fric_stop = speed**2 / (0.004)
            # How much time it will take to rotate from the target
            rot_time = (180)/self.dAng
            stop_speed = (0.001+self.dSpeed)
            # Distance to pass with rotation thruster slow down until speed=0
            rot_stop_dist = -(-(self.dSpeed*rot_time)**2/stop_speed
                              + (self.dSpeed*rot_time/stop_speed)*(2*self.dSpeed*rot_time - speed)
                              - self.dSpeed*rot_time**2)
            # if can stop with friction
            if dist > fric_stop:
                ang = Utils.angle_diff(self.ang, ang_goal)
            # if can stop with rotation and burn
            elif dist > rot_stop_dist:
                ang = Utils.angle_diff(self.ang, ang_goal)
            # Slow down by rotation and burn
            else:
                ang_goal = ang_goal - 180
                ang = Utils.angle_diff(self.ang, ang_goal)
            # Rotate toward a goal
            if abs(ang) > 0:
                if abs(ang) > self.dAng:
                    self.rotate(np.sign(ang) * self.dAng)
                    ang += -np.sign(ang) * self.dAng
                else:
                    self.rotate(ang)
                    ang = 0
            # Accelerate if inline with a goal
            if abs(ang) <= 1:
                self.accelerate(self.dSpeed, self.ang)
                g= pg.Rect(self.rect.x+100*np.sin((ang_goal-180)/180*np.pi),
                           self.rect.y+100*np.cos((ang_goal-180)/180*np.pi),
                           10, 10)
                Classes.FXLaser(self.rect, g, 5, 5, 5, (255,50,50), (0,0), self.sector)
            self._prev_dist = dist
            return False
        # Success
        else:
            self._prev_dist = None
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


class ShipGenerator:
    def generate_specific(self, size, tech, shape) -> Ship:
        raise NotImplementedError()

    @staticmethod
    def generate_test():
        ship = Ship([], (1, 1))  # Start in the middle of the screen
        M.Propulsion(1, 0.1, 1, max_speed=3).assignShip(ship).place(0, 50)
        M.Hull(5).assignShip(ship).place(0, 10)
        M.Capacitor(1, 5).assignShip(ship).place(40, 0)
        M.Generator(1, 1).assignShip(ship).place(-40, 0)
        M.Weapon(1, 1).assignShip(ship).place(0, -40)
        ship.updateSystem()
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
