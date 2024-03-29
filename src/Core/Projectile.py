import copy
import random

import numpy as np

from Utils import dict_hash
from Core.Mechanics import GObject, Vulnerable, Animation
import Core.State as State


class Projectile(GObject, Vulnerable):
    def __init__(self, img, x, y, distance, width=None, height=None,
                 damage=None,
                 max_velocity=None,
                 expl_ref=None,
                 env_friction=0,
                 mass=0.1, **kwargs):
        super().__init__(img, x, y, width=width, height=height, mass=mass, env_friction=env_friction, **kwargs)

        Vulnerable.__init__(self, damage)
        self.velocity_max = max_velocity
        self.timer = distance
        self.expl_ref = expl_ref

        # movable.add(self)
        self.state.projectiles.add(self)
        self.state.time_dependent.add(self)

    def remove(self):
        self.kill()

    def damage(self, obj):
        buff = copy.copy(obj.hp)
        obj.damage(self.hp)
        self.hp += -buff
        expl_animation = random.choice(self.state.buff_explosions[self.expl_ref])
        Animation.FX_explosion(self.rect.centerx, self.rect.centery, expl_animation, randdir=False, state=self.state)
        if self.hp < 0:
            self.kill()
            self.hp = 0

    # it is assumed to be a bolt the projectile is constructed here
    @staticmethod
    def shot(self, direction, bolt):
        skipped_len = self.rect.height // 2
        expl_ref = dict_hash(State.projectile_types[bolt]['expl_params'])
        shot = Projectile(State.projectile_types[bolt]['image'],
                          self.rect.centerx,
                          self.rect.centery,
                          damage=State.projectile_types[bolt]['damage'],
                          distance=State.projectile_types[bolt]['distance'],
                          max_velocity=State.projectile_types[bolt]['velocity'],
                          expl_ref=expl_ref,
                          state=self.state
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

        shot.v = [State.projectile_types[bolt]['velocity']
                  * np.cos(np.deg2rad(self.look_dir - 90)),
                  State.projectile_types[bolt]['velocity']
                  * np.sin(np.deg2rad(self.look_dir - 90))]
        return shot