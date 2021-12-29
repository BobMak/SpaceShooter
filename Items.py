from Mechanics import GObject, FX_Glow
from Assets import live
import State


class Item(GObject):
    IMAGES = [
        State.missile_types['heavy_missile']['image'],
        live]

    def __init__(self, type, x, y):
        super().__init__(Item.IMAGES[type], x, y, width=None, height=None)
        State.pickupables.add(self)
        State.effects.add(self)
        self.brightness = 0.03
        self.radius_min = 10
        self.radius_max = 30
        self.radius = 10
        self.radius_float = 10
        self.radius_delta = 0.3
        self.color = (0, 0, 0)

    def pickup(self, player):
        State.pickupables.remove(self)
        State.effects.remove(self)

    def update(self):
        self.radius_float += self.radius_delta
        self.radius = int(self.radius_float)
        if self.radius > self.radius_max or self.radius < self.radius_min:
            self.radius_delta = -self.radius_delta
        FX_Glow(self.rect, 1, self.radius // 2, int(self.radius),
                (self.color[0], self.color[1], self.color[2], int(self.brightness * 255)))


class MissileItem(Item):
    def __init__(self, x, y, n):
        super().__init__(0, x, y)
        self.nubmer = n
        self.color = (255, 50, 50)

    def pickup(self, player):
        player.addMissiles(self.nubmer)
        super().pickup(player)


