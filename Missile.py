import random

from Mechanics import *
from Zone import Zone
from Projectile import Projectile
import Funcs


class Missile(Projectile):
    # how often aim-updaing function to run
    def __init__(self, bolt, x, y):
        super().__init__(bolt + State.n_bolts, x, y, State.msl_distances[bolt])
        self.compute_tempo = 5
        self.compute_count = 0
        self.d_ang = State.msl_d_angs[bolt]
        self.d_speed = State.msl_d_speeds[bolt]
        self.max_speed = State.msl_max_speeds[bolt]
        self.hit_range = State.msl_hit_ranges[bolt]
        self.hp = State.bolt_damage[bolt + State.n_bolts]
        self.mod_speed = 0
        self.dist_prev = 500
        self.dist = None
        State.missiles.add(self)
        State.projectiles.remove(self)

        self.aim = self.lock_closest()

    def rotate_to_aim(self):

        aim_dir = self.get_aim_dir(self.aim)

        x = (self.look_dir - aim_dir)

        if abs(x) > 180:
             self.rotate(self.d_ang*np.sign(x))
        else:
            self.rotate(-self.d_ang*np.sign(x))

    def lock_closest(self):
        arr = []
        for x in State.asteroids:
            arr.append(self.get_distance(x))
        if len(arr) > 0:
            return State.asteroids.sprites()[arr.index(min(arr))]
        else:
            return None

    def pursue(self):

        r = copy.copy(self.rect)

        # create engine particles
        FX_Track(particle, r, 40, look_dir=random.randint(0,358),
                        fading=[20,16], enlarging=[20,16],
                        color=(200,200,200,random.randint(40,130)),
                        speed=[random.uniform(-0.5,0.5), random.uniform(-0.5,0.5)])

        FX_Glow(r, 1, 2, 10, (255, 200, 125, 20))

        self.rotate_to_aim()
        self.mod_speed += self.d_speed

        # If missile is close enough to aim but fails to hit it (starts to get
        # further from aim), missile will detonate.
        self.dist = self.get_distance(self.aim)
        if self.dist > self.dist_prev and self.dist < self.hit_range:
            self.blow_up()
            return
        self.dist_prev = self.dist

        a1 = self.speed[0] + self.d_speed*np.cos(np.deg2rad(self.look_dir-90))
        if a1 < self.max_speed and a1 > -self.max_speed:
            self.speed[0] = a1
        else:
            self.speed[0] = self.max_speed*np.cos(np.deg2rad(self.look_dir-90))

        a2 = self.speed[1] + self.d_speed*np.sin(np.deg2rad(self.look_dir-90))
        if a2 < self.max_speed and a2 > -self.max_speed:
            self.speed[1] = a2
        else:
            self.speed[1] = self.max_speed*np.sin(np.deg2rad(self.look_dir-90))

    def update(self):

        if self.aim in State.asteroids:
            self.pursue()
        else:
            self.aim = self.lock_closest()

        self.compute_count += 1
        if self.compute_count > self.compute_tempo:
            self.compute_count = 0
            self.aim = self.lock_closest()

    def blow_up(self):

        x = Zone(self.rect.x, self.rect.y, self.hit_range, self.hp, 2)
        Animation.FX_explosion(self.rect.centerx, self.rect.centery,
                       xpl=expN, radius=(60,60))
        State.hit_waves.add(x)
        State.time_dependent.add(x)
        self.kill()

