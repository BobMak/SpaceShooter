import Utils
from Core.Mechanics import *

from Core.Projectile import Projectile


class Ship(GObject, Vulnerable):
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
                 env_friction=0,
                 acceleration=0,
                 complex_sh=(),
                 width=None,
                 height=None,
                 mass=1,
                 state=None):

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
        self.rotation_rate = rotation_rate / 100
        self.rotation_rate_max = rotation_rate
        self.acceleration = acceleration
        self.deacceleration = deacceleration
        self.env_deacceleration = env_friction
        self.max_acceleration_reserve = max_acceleration_reserve
        self.acceleration_reserve_regeneration = acceleration_reserve_regeneration
        self.acceleration_burn_rate = acceleration_burn_rate

        self.acceleration_reserve = copy.deepcopy(self.max_acceleration_reserve)
        self.hp = copy.deepcopy(self.max_hp)
        self.shield_hp = copy.deepcopy(self.max_shield_hp)
        self.v = [0,0]
        GObject.__init__(
            self, image, x, y, width=width, height=height,
            env_friction=env_friction,
            mass=mass,
            state=state
        )
        Vulnerable.__init__(self, hp)

        self.bolt = bolt
        self.missiles = 0

        self.time_count_fire = 0
        self.timer_fire = State.projectile_types[bolt]['cooldown']

        self.time_count_special = 0
        self.timer_special = state.spec_cooldown[0]

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

        # control flags. Determine if the automatic rotation and acceleration
        # stabilizers should be applied.
        self.target_rotation = self.look_dir
        self.isrotating = False

    def addMissiles(self, number):
        self.missiles += number

    def destroy(self):
        self.kill()
        self.v = [0,0]

        Animation.FX_explosion(self.rect.centerx, self.rect.centery, state=self.state)

        for x in self.shields:
            x.down()

        for x in [*self.mounts, *self.shields, *self.hull_group]:
            x.kill()

    def damage(self, dmg, moving=None):
        self.hp += -max(0, dmg)
        if self.hp < 0:
            self.destroy()

        if moving:
            self.rigid_collision(moving)

    def m_add(self, mounted):
        self.mounts.append(mounted)

    def sh_add(self, shield):
        self.shields.add(shield)

    def scan(self):
        min_dist = self.state.asteroids.sprites[0]

        for i in self.state.asteroids:
            dist = np.sqrt((self.pos[0] - i.pos[0])**2
                         + (self.pos[1] - self.pos[1])**2)
            if dist < min_dist:
                min_dist = dist

        return min_dist

    def fire(self):
        if self.locks[0] == False:
            self.locks[0] = True
            Projectile.shot(self, self.look_dir, self.bolt)

    def accelerate(self, temp, manual=True):
        if manual:
            self.isaccelerating = True
        if not self.acceleration_reserve < 0.4:
            self.acceleration_reserve = max(0.0, self.acceleration_reserve - self.acceleration_burn_rate)
            super().accelerate_forward(temp)
        else:
            self.acceleration_lock = True

    def rotate(self, ang, manual=True):
        # super().rotate(ang)
        if manual:
            self.isrotating = True
            self.target_rotation = self.look_dir
        self.rotation_rate = np.min([self.rotation_rate_max, self.rotation_rate + self.rotation_rate_max/30])
        sign = np.sign(ang)
        super().apply_force_angular(self.rotation_rate*sign)
        for x in self.turrets:
            x.apply_force_angular(self.rotation_rate)
            Utils.orbit_rotate(self, x, -self.rotation_rate * sign,
                               x.distance, x.orbit_ang)

        for x in self.shields:
            x.apply_force_angular(self.rotation_rate*sign)

        for x in self.hull_group:
            Utils.orbit_rotate(self, x, -self.rotation_rate * sign,
                               x.distance, x.orbit_ang)

    def stabilize(self):
        """if the user is not rotating, the ship should stick to the current
        rotation angle and position"""
        if not self.isrotating and self.av != 0:
            diff_ang = self.target_rotation - self.look_dir
            if diff_ang > 180:
                diff_ang -= 360
            if diff_ang < -180:
                diff_ang += 360
            diff_avel = self.av
            super().apply_force_angular(
                + diff_ang * self.rotation_rate_max / 10
                - diff_avel * self.rotation_rate_max
            )

    def draw_rotating(self):
        super().draw_rotating()
        for x in self.shields:
            x.draw_rotating()

    def update(self):
        self.acceleration_reserve = min(self.max_acceleration_reserve,
                                        self.acceleration_reserve_regeneration + self.acceleration_reserve)
        self.stabilize()
        for n in range(len(self.locks)):
            if self.locks[n]:
                self.counts[n] += 1
                if self.timers[n] < self.counts[n]:
                    self.counts[n] = 0
                    self.locks[n] = False

        self.isrotating = False
