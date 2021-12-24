import random
import pygame

import State
from Assets import particle, asteroid_imgs, bad_thing
from Mechanics import GObject, Moving, Vulnerable, FX_Track

from Agressor import Agressor


class Asteroid(GObject, Moving, Vulnerable):
    noclip_count =0
    noclip_timer = 30
    velo_deviation = 1
    density = (1,2)

    def __init__(self, image, x, y, type, speed):

        super().__init__(pygame.transform.scale(image, (10*type, 10*type)),
                        x, y, width=type*10, height=type*10)

        Moving.__init__(self)
        Vulnerable.__init__(self, 1)

        self.type = type
        State.asteroids.add(self)
        self.image = pygame.transform.scale(image, (10*type, 10*type))
        self.speed = [speed[0] + random.uniform(-self.velo_deviation,
                                                 self.velo_deviation),
                      speed[1] + random.uniform(-self.velo_deviation,
                                                 self.velo_deviation)]
        self.look_dir = (random.random() - 0.5) * 360
        self.hp = self.type * 2

        # movable.add(self)
        State.asteroids.add(self)
        self.rotate(0)

    def crash(self):
        if self.type >2:
            for x in range(6):
                FX_Track(particle, self.rect, 50,
                         look_dir=(random.randint(0,350)),
                         speed=[self.speed[0] + random.uniform(-1,1),
                                self.speed[1] + random.uniform(-1,1)],
                         color=(120,100,100,150))

        if self.type > 1:
            arr = []
            for i in range(random.choice(self.density)):

                i = Asteroid(self.image,
                    self.rect.centerx, self.rect.centery, self.type-1, self.speed)

                arr.append(i)

                if random.choice((1,0)):
                    i.speed[0] = -self.speed[0]
                else:
                    i.speed[1] = -self.speed[1]

            return arr
        self.kill()

    def update(self):
        self.noclip_count += 1
        if self.noclip_count > self.noclip_timer:
            self.noclip_count = 0
            State.noclip_asteroids.remove(self)


class AdvAsteroid(Asteroid):

    def __init__(self, level, x, y, type, speed):

        super().__init__(asteroid_imgs[level-1], x, y, type, speed)
        self.level = level
        self.hp = State.asteroid_hps[level-1] * self.type
        self.noclip_timer = State.asteroid_noclip_timers[level-1]
        self.density = State.asteroid_densities[level-1]
        self.velo_deviation = State.asteroid_velocity_deviations[level-1]

    def damage(self, dmg, type=None, speed=None):

        self.hp += -max(0, dmg)

        rect = pygame.Rect(self.rect.x, self.rect.y,
                           self.type*10+10, self.type*10+10)

        if type != None:
            self.speed = [self.speed[0] + speed[0]*((type+1)/(self.type+1)),
                          self.speed[1] + speed[1]*((type+1)/(self.type+1))]

        if self.hp < 0:
            self.crash()
            return

    def crash(self):
        if self.type >2:
            for x in range(6):
                FX_Track(particle, self.rect, random.randint(20,80),
                         look_dir=(random.randint(0,350)),
                         speed=[self.speed[0] + random.uniform(-1,1),
                                self.speed[1] + random.uniform(-1,1)],
                         color=(random.randint(90,200),100,100,150))

        if self.type > 1:
            arr = []
            for i in range(random.choice(self.density)):

                x = AdvAsteroid(self.level, self.rect.centerx,
                                self.rect.centery, self.type - 1, self.speed)
                arr.append(i)

                if random.choice((1,0)):
                    x.speed[0] = -self.speed[0]
                else:
                    x.speed[1] = -self.speed[1]

                if random.choice((0,0,0,0,0,0,0,0,1)):
                    c = Agressor(bad_thing, self.rect.centerx, self.rect.centery)
                    c.remove(State.player_group)
                    try:
                        c.rush()
                    except:
                        pass

        self.kill()