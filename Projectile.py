import copy

import numpy as np

from Assets import prj_imgs
from Mechanics import GObject, Moving, Vulnerable
import State


class Projectile(GObject, Moving, Vulnerable):
    def __init__(self, bolt, x, y, distance, width=None, height=None):
        super().__init__(prj_imgs[bolt], x, y, width=width, height=height)
        Moving.__init__(self)
        Vulnerable.__init__(self, State.bolt_damage[bolt])

        self.speed_max = State.prj_speeds[bolt]
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

    @staticmethod
    def shot(self, direction, bolt):
        skipped_len = self.rect.height // 2
        shot = Projectile(bolt, self.rect.centerx,
                          self.rect.centery, State.prj_distances[bolt])
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

        shot.speed = [State.prj_speeds[bolt]
                      * np.cos(np.deg2rad(self.look_dir - 90)),
                      State.prj_speeds[bolt]
                      * np.sin(np.deg2rad(self.look_dir - 90))]
        shot.rotate(0)