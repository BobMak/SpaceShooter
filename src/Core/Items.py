from Core.Mechanics import GObject, FX_Glow
from Core.Assets import live
import Core.State as State


class Item(GObject):
    IMAGES = [
        State.missile_types['heavy_missile']['image'],
        live]

    def __init__(self, type, x, y, state=None):
        super().__init__(Item.IMAGES[type], x, y, width=None, height=None, state=state)
        state.pickupables.add(self)
        state.effects.add(self)
        self.brightness = 0.03
        self.radius_min = 10
        self.radius_max = 30
        self.radius = 10
        self.radius_float = 10
        self.radius_delta = 0.3
        self.color = (0, 0, 0)

    def pickup(self, player):
        self.state.pickupables.remove(self)
        self.state.effects.remove(self)

    def update(self):
        self.radius_float += self.radius_delta
        self.radius = int(self.radius_float)
        if self.radius > self.radius_max or self.radius < self.radius_min:
            self.radius_delta = -self.radius_delta
        FX_Glow(self.rect, 1, self.radius // 2, int(self.radius),
                (self.color[0], self.color[1], self.color[2], int(self.brightness * 255)),
                state=self.state)


class MissileItem(Item):
    def __init__(self, x, y, n, state=None):
        super().__init__(0, x, y, state=state)
        self.nubmer = n
        self.color = (255, 50, 50)

    def pickup(self, player):
        player.addMissiles(self.nubmer)
        super().pickup(player)


