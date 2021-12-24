import copy

import numpy as np

from Mechanics import GObject, Moving, Vulnerable
import State


class Projectile(GObject, Moving, Vulnerable):
    def __init__(self, img, x, y, distance, width=None, height=None,
                 damage=None,
                 max_speed=None):
        super().__init__(img, x, y, width=width, height=height)
        Moving.__init__(self)

        Vulnerable.__init__(self, damage)
        self.speed_max = max_speed
        self.timer = distance

        # movable.add(self)
        State.projectiles.add(self)
        State.time_dependent.add(self)

    def remove(self):
        self.kill()

    def damage(self, obj):
        buff = copy.copy(obj.hp)
        obj.damage(self.hp)
        self.hp += -buff
        if self.hp < 0:
            self.kill()
            self.hp = 0

    # it is assumed to be a bolt the projectile is constructed here
    @staticmethod
    def shot(self, direction, bolt):
        skipped_len = self.rect.height // 2
        shot = Projectile(State.projectile_types[bolt]['image'],
                          self.rect.centerx,
                          self.rect.centery,
                          damage=State.projectile_types[bolt]['damage'],
                          distance=State.projectile_types[bolt]['distance'],
                          max_speed=State.projectile_types[bolt]['speed'],
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

        shot.speed = [State.projectile_types[bolt]['speed']
                      * np.cos(np.deg2rad(self.look_dir - 90)),
                      State.projectile_types[bolt]['speed']
                      * np.sin(np.deg2rad(self.look_dir - 90))]
        shot.rotate(0)
        return shot