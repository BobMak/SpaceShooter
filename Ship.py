import Funcs
from Funcs import blur
from Mechanics import *

from Projectile import Projectile


class Ship(GObject, Moving, Vulnerable):
    '''Player(image, x, y, lives, bolt=0,
              complex_sh=-1, width=None, height=None)'''

    def __init__(self, image,
                 x, y,
                 hp,
                 shield=0,
                 rotation_rate=3,
                 bolt='',
                 missile='',
                 max_acceleration_reserve=0,
                 acceleration_burn_rate=0,
                 acceleration_reserve_regeneration=0,
                 deacceleration=0,
                 env_deacceleration=0,
                 acceleration=0,
                 complex_sh=(), width=None, height=None):

        self.bolt = bolt
        self.missile = missile
        self.arr_input = []
        self.shields_orbit_group = pygame.sprite.Group()
        self.shields = pygame.sprite.Group()
        self.turrets = pygame.sprite.Group()
        self.orbiting = pygame.sprite.Group()
        self.mounts = []

        self.hull_group_ang = 0

        self.space_lock = False
        self.special_lock = False
        self.missile_lock = False
        self.shield_lock = False
        self.acceleration_lock = False
        self.locks = [self.space_lock, self.special_lock, self.missile_lock, self.shield_lock, self.acceleration_lock]

        self.max_hp = hp
        self.max_shield_hp = shield
        self.rotation_rate = rotation_rate
        self.acceleration = acceleration
        self.deacceleration = deacceleration
        self.env_deacceleration = env_deacceleration
        self.max_acceleration_reserve = max_acceleration_reserve
        self.acceleration_reserve_regeneration = acceleration_reserve_regeneration
        self.acceleration_burn_rate = acceleration_burn_rate

        self.acceleration_reserve = copy.deepcopy(self.max_acceleration_reserve)
        self.hp = copy.deepcopy(self.max_hp)
        self.shield_hp = copy.deepcopy(self.max_shield_hp)
        self.speed = [0,0]
        GObject.__init__(self, image, x, y, width=width, height=height)
        Moving.__init__(self)
        Vulnerable.__init__(self, hp)

        self.bolt = bolt
        self.missiles = 0

        self.time_count_fire = 0
        self.timer_fire = State.projectile_types[bolt]['cooldown']

        self.time_count_special = 0
        self.timer_special = State.spec_cooldown[0]

        self.time_count_missile = 0
        self.timer_missile = State.missile_types[missile]['cooldown']

        self.time_count_shield = 0
        self.timer_shield = 50

        self.time_count_acceleration = 0
        self.timer_acceleration = 50

        self.counts = [self.time_count_fire, self.time_count_special,
                       self.time_count_missile, self.time_count_shield]

        self.timers = [self.timer_fire, self.timer_special,
                       self.timer_missile, self.timer_shield]

        self.hull_group = pygame.sprite.Group()
        for x in complex_sh:
            b = Colliding(x[0], x[1], x[2], x[3], self)
            self.hull_group.add(b)

        self.distance = 0
        self.orbit_ang = 0

    def addMissiles(self, number):
        self.missiles += number

    def destroy(self):
        self.kill()
        self.rotate(0)
        self.speed = [0,0]

        Animation.FX_explosion(self.rect.centerx, self.rect.centery)

        for x in self.shields:
            x.down()

        for x in [*self.mounts, *self.shields, *self.hull_group]:
            x.kill()

    def damage(self, dmg):
        self.hp += -max(0, dmg)
        if self.hp < 0:
            self.destroy()

    def m_add(self, mounted):
        self.mounts.append(mounted)

    def sh_add(self, shield):
        self.shields.add(shield)

    def scan(self):
        min_dist = State.asteroids.sprites[0]

        for i in State.asteroids:
            dist = np.sqrt((self.rect.x - i.rect.x)**2
                         + (self.rect.y - i.rect.y)**2)
            if dist < min_dist:
                min_dist = dist

        return min_dist

    def fire(self):
        if self.locks[0] == False:
            self.locks[0] = True
            Projectile.shot(self, self.look_dir, self.bolt)

    def accelerate(self, temp):
        if not self.acceleration_reserve < 0.4:
            self.acceleration_reserve = max(0.0, self.acceleration_reserve - self.acceleration_burn_rate)
            super()._accelerate(temp)
        else:
            self.acceleration_lock = True

    def rotate(self, ang):
        super().rotate(ang)
        for x in self.turrets:
            x.rotate(self.rotation_rate)
            Funcs.orbit_rotate(self, x, -self.rotation_rate,
                               x.distance, x.orbit_ang)

        for x in self.shields:
            x.rotate(self.rotation_rate)

        for x in self.hull_group:
            Funcs.orbit_rotate(self, x, -self.rotation_rate,
                               x.distance, x.orbit_ang)

    def draw_rotating(self):
        super().draw_rotating()
        speed = np.sqrt(self.speed[0] ** 2 + self.speed[1] ** 2)
        if speed > 8:
            blur(self, speed)
        for x in self.shields:
            x.draw_rotating()

    def update(self):
        self.acceleration_reserve = min(self.max_acceleration_reserve,
                                        self.acceleration_reserve_regeneration + self.acceleration_reserve)

        for n in range(len(self.locks)):
            if self.locks[n]:
                self.counts[n] += 1
                if self.timers[n] < self.counts[n]:
                    self.counts[n] = 0
                    self.locks[n] = False
