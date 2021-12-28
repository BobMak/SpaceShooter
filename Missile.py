import time

from Mechanics import *
from Zone import Zone
from Projectile import Projectile


class Missile(Projectile):
    # how often aim-updaing function to run
    def __init__(self, img, x, y,
                 distance=0,
                 rotation_speed=0.0,
                 max_speed=0,
                 damage=0,
                 acceleration=0,
                 hit_range=0,
                 expl_params=None,):
        super().__init__(img, x, y,
                         distance=distance,
                         max_speed=max_speed,
                         damage=damage,
                         )
        self.compute_tempo = 5
        self.compute_count = 0
        self.d_ang =     rotation_speed
        self.d_speed =   acceleration
        self.max_speed = max_speed
        self.hit_range = hit_range
        self.expl_params = expl_params
        self.hp =        damage

        self.mod_speed = 0
        self.dist_prev = 500
        self.dist = None
        State.missiles.add(self)
        State.projectiles.remove(self)

        self.aim = self.lock_closest()
        self.expAnimation = None

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
                        fading=(20,16), enlarging=(20,16),
                        color=(200,200,200,random.randint(40,130)),
                        speed=[random.uniform(-0.5,0.5), random.uniform(-0.5,0.5)])

        brightness = max(0.0, random.gauss(0.5, 0.2))
        FX_Glow(r, 1, int(20 * brightness), int(20 * brightness), (255, 200, 125, int(brightness * 10)))

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
        if a1 >= self.max_speed or a1 <= -self.max_speed:
            a1 = self.max_speed*np.cos(np.deg2rad(self.look_dir-90))

        a2 = self.speed[1] + self.d_speed*np.sin(np.deg2rad(self.look_dir-90))
        if a2 >= self.max_speed or a2 <= -self.max_speed:
            a2 = self.max_speed*np.sin(np.deg2rad(self.look_dir-90))

        self.speed = (a1, a2)

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
        prm_hash = dict_hash(self.expl_params)
        if self.expAnimation:
            explAnimation = self.expAnimation
        elif prm_hash in State.buff_explosions:
            explAnimation = random.choice(State.buff_explosions[prm_hash])
        else:
            while not prm_hash in State.buff_explosions:
                time.sleep(0.1)
            explAnimation = random.choice(State.buff_explosions[prm_hash])
        Animation.FX_explosion(self.rect.centerx, self.rect.centery,
                       xpl=explAnimation, radius=(self.hit_range*3,self.hit_range*3), randdir=False)
        State.hit_waves.add(x)
        State.time_dependent.add(x)
        self.kill()

    @staticmethod
    def shot(self, direction, missile):
        def _delayed_action():
            skipped_len = self.rect.height // 2
            for _ in range(State.missile_types[missile]['volley']):
                # don't shoot if the launches is dead
                if self.hp <= 0:
                    return
                shot = Missile(State.missile_types[missile]['image'],
                                  self.rect.centerx,
                                  self.rect.centery,
                                  damage=State.missile_types[missile]['damage'],
                                  distance=State.missile_types[missile]['distance'],
                                  max_speed=State.missile_types[missile]['speed'],
                                  acceleration=State.missile_types[missile]['acceleration'],
                                  rotation_speed=State.missile_types[missile]['rotation_speed'],
                                  hit_range=State.missile_types[missile]['hit_range'],
                                  expl_params=State.missile_types[missile]['expl_params'],
                               )
                if direction:
                    shot.look_dir = direction
                else:
                    shot.look_dir = self.look_dir
                shot.rect.centerx = (self.rect.centerx
                                     - skipped_len * np.cos(np.deg2rad(shot.look_dir
                                                                       + 90)))
                shot.rect.centery = (self.rect.centery
                                     - skipped_len * np.sin(np.deg2rad(shot.look_dir
                                                                       + 90)))

                shot.speed = [State.missile_types[missile]['speed']
                              * np.cos(np.deg2rad(self.look_dir - 90)),
                              State.missile_types[missile]['speed']
                              * np.sin(np.deg2rad(self.look_dir - 90))]
                shot.rotate(0)
                # delay between shots
                time.sleep(0.2)
        # fire missiles in thread so they can be fired with a delay
        threading.Thread(target=_delayed_action).start()
