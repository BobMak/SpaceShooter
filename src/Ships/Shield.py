from Core import Assets, State
from Core.Mechanics import Animation


class Shield(Animation):
    def __init__(self, images_arr, width, height, x, y, source, type=0, state=None):
        super().__init__(images_arr, width, height, x, y, type, state=state)
        self.source = source
        self.v = source.v
        self.type = type
        self.HP = source.shield_hp

        self.rect.width = width
        self.rect.height = height
        self.rect.centerx = source.rect.centerx
        self.rect.centery = source.rect.centery

        source.shields.add(self)

    def update(self):
        self.rect.centerx = self.source.rect.centerx
        self.rect.centery = self.source.rect.centery

    def down(self):
        self.type = 3
        self.source.locks[3] = True
        self.kill()

    def damage(self, dmg, moving=None):
        global shield_lock
        self.HP += -max(0, dmg)

        if self.HP < 0:
            self.down()

        if moving:
            self.source.rigid_collision(moving)

    @staticmethod
    def shields(source):
        if len(source.shields) == 0:
            shld_obj = Shield(Assets.shield, source.rect.width + 10,
                              source.rect.height + 10, source.rect.left,
                              source.rect.top, source, 1,
                              state=source.state)

            # shld_obj.rotate(source.look_dir)
            source.sh_add(shld_obj)
            source.state.effects.add(shld_obj)
