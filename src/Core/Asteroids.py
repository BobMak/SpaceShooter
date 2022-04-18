import random
import pygame

import Core.State as State
from Core.Assets import particle, asteroid_imgs, bad_thing
from Core.Mechanics import GObject, Vulnerable, FX_Track

from Entities.Chaser import Chaser


class Asteroid(GObject, Vulnerable):
    noclip_count =0
    noclip_timer = 30
    velo_deviation = 1
    density = (1,2)

    def __init__(self, image, x, y, type, velocity, state=None):

        super().__init__(
            pygame.transform.scale(image, (10*type, 10*type)),
            x, y, width=type*10, height=type*10,
            mass=type*5,
            env_friction=0.0001,
            angular_velocity=random.uniform(-0.5, 0.5),
            state=state
        )

        Vulnerable.__init__(self, 1)

        self.state = state
        self.type = type
        self.state.asteroids.add(self)
        self.image = pygame.transform.scale(image, (10*type, 10*type))
        self.v = [velocity[0] + random.uniform(-self.velo_deviation,
                                                      self.velo_deviation),
                         velocity[1] + random.uniform(-self.velo_deviation,
                                                   self.velo_deviation)]
        self.look_dir = (random.random() - 0.5) * 360
        self.hp = self.type * 2

        self.state.asteroids.add(self)

    def crash(self):
        if self.type >2:
            for x in range(6):
                FX_Track(particle, self.rect, 50,
                         look_dir=(random.randint(0,350)),
                         velocity=[self.v[0] + random.uniform(-1, 1),
                                   self.v[1] + random.uniform(-1, 1)],
                         color=(120,100,100,150),
                         state=self.state)

        if self.type > 1:
            arr = []
            for i in range(random.choice(self.density)):

                i = Asteroid(self.image,
                             self.rect.centerx, self.rect.centery, self.type - 1, self.v, state=self.state)

                arr.append(i)

                if random.choice((1,0)):
                    self.v[0] = -self.v[0]
                else:
                    self.v[1] = -self.v[1]

            return arr
        self.kill()

    def update(self):
        self.noclip_count += 1
        if self.noclip_count > self.noclip_timer:
            self.noclip_count = 0
            self.state.noclip_asteroids.remove(self)


class AdvAsteroid(Asteroid):

    def __init__(self, level, x, y, type, velocity, state=None):

        super().__init__(asteroid_imgs[level-1], x, y, type, velocity, state=state)
        self.level = level
        self.hp = State.waves[level - 1]["hps"] * self.type
        self.noclip_timer = State.waves[level - 1]["noclip_timers"]
        self.density = State.waves[level - 1]["densities"]
        self.velo_deviation = State.waves[level - 1]["velocity_deviations"]

    def damage(self, dmg, type=None, velocity=None, moving=None):

        self.hp += -max(0, dmg)

        # rect = pygame.Rect(self.pos[0], self.pos[1],
        #                    self.type*10+10, self.type*10+10)

        if type != None:
            self.v = [self.v[0] + velocity[0] * ((type + 1) / (self.type + 1)),
                             self.v[1] + velocity[1] * ((type + 1) / (self.type + 1))]

        # if the colliding object is moving, calculate the change in velocity
        if moving != None:
            self.rigid_collision(moving)

        if self.hp < 0:
            self.crash()
            return

    def crash(self):
        if self.type >2:
            for x in range(6):
                FX_Track(particle, self.rect, random.randint(20,80),
                         look_dir=(random.randint(0,350)),
                         velocity=[self.v[0] + random.uniform(-1, 1),
                                   self.v[1] + random.uniform(-1, 1)],
                         color=(random.randint(90,200),100,100,150),
                         state=self.state)

        if self.type > 1:
            arr = []
            for i in range(random.choice(self.density)):

                x = AdvAsteroid(self.level, self.rect.centerx,
                                self.rect.centery, self.type - 1, self.v, state=self.state)
                arr.append(i)

                if random.choice((0,0,0,0,0,0,0,0,1)):
                    c = Chaser(bad_thing, self.rect.centerx, self.rect.centery, state=self.state)
                    c.remove(self.state.player_group)
                    try:
                        c.rush()
                    except:
                        pass

        self.kill()

    def prep_animations(self):
        pass