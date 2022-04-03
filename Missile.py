import time

from Mechanics import *
from Zone import Zone
from Projectile import Projectile


class Missile(Projectile):
    # how often aim-updaing function to run
    def __init__(self, img, x, y,
                 distance=0,
                 rotation_velocity=1.0,
                 max_velocity=3.0,
                 damage=0,
                 thrust=1.0,
                 hit_range=0,
                 expl_params=None,
                 mass=1):
        super().__init__(img, x, y,
                         distance=distance,
                         max_velocity=max_velocity,
                         damage=damage,
                         mass=mass,
                         env_friction=0.3
                         )
        self.compute_period = 5
        self.compute_count = 0
        self.d_ang =        rotation_velocity
        self.thrust =       thrust
        self.max_velocity = max_velocity
        self.hit_range = hit_range
        self.expl_params = expl_params
        self.hp =        damage

        self.mod_velocity = 0
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
            print(self, 'rotating right')
            self.apply_force_angular(self.d_ang*np.sign(x))
        else:
            print(self, 'rotating left')
            self.apply_force_angular(-self.d_ang*np.sign(x))

    def lock_closest(self):
        mindist = 1e10
        aim = None
        for x in State.asteroids:
            if self.get_distance(x) < mindist:
                mindist = self.get_distance(x)
                aim = x
        return aim

    def pursue(self):
        r = copy.copy(self.rect)
        # create engine particles
        FX_Track(particle, r, 40, look_dir=random.randint(0,358),
                 fading=(20,16), enlarging=(20,16),
                 color=(200,200,200,random.randint(40,130)),
                 velocity=[random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)])

        brightness = max(0.0, random.gauss(0.5, 0.2))
        FX_Glow(r, 1, int(20 * brightness), int(20 * brightness), (255, 200, 125, int(brightness * 10)))

        self.rotate_to_aim()
        self.mod_velocity += self.thrust

        # If missile is close enough to aim but fails to hit it (starts to get
        # further from aim), missile will detonate.
        self.dist = self.get_distance(self.aim)
        if self.dist > self.dist_prev and self.dist < self.hit_range:
            self.blow_up()
            return
        self.dist_prev = self.dist

        # if np.sqrt(self.v[0]**2 + self.v[1]**2) < self.max_velocity:
        self.accelerate_forward(self.thrust)

    def update(self):

        if self.aim:
            self.pursue()
        else:
            self.aim = self.lock_closest()

        self.compute_count += 1
        if self.compute_count > self.compute_period:
            self.compute_count = 0
            self.aim = self.lock_closest()

    def blow_up(self):
        x = Zone(self.pos[0], self.pos[1], self.hit_range, self.hp, 2)
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
                               max_velocity=State.missile_types[missile]['velocity'],
                               thrust=State.missile_types[missile]['acceleration'],
                               rotation_velocity=State.missile_types[missile]['rotation_velocity'],
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

                shot.v = [State.missile_types[missile]['velocity']
                                 * np.cos(np.deg2rad(self.look_dir - 90)),
                                 State.missile_types[missile]['velocity']
                                 * np.sin(np.deg2rad(self.look_dir - 90))]
                # delay between shots
                time.sleep(0.2)
        # fire missiles in thread so they can be fired with a delay
        threading.Thread(target=_delayed_action).start()
