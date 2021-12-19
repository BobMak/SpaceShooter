from Mechanics import *
from Mounted import Mounted


class Turret(Mounted):
    """Turret(image, radius, mounted_on, groups = None,
              distance = 20, look_dir = 0,
              width = 20, height = 20,
              restriction = None, bg = bg_ball)
    """
    interesting = [State.asteroids]
    in_range = []

    def __init__(self, image, radius, mounted_on,
                groups = None, distance = 20, look_dir = 0,
                width = 20, height = 20, restriction = None, bg = bg_ball):

        super().__init__(image, mounted_on, distance, look_dir,
                        width, height, restriction)
        self.radius = radius
        self.locked = None
        self.bg = pygame.transform.scale(bg, (width-6, height-6))
        self.bg_rect = bg.get_rect()
        # self.bg_rect = bg.get_rect()


        if groups != None:
            for i in groups:
                self.interesting.append(i)

    def set_priorities(self, group):
        b = self.interesting.pop(State.interesting.index('group'))
        self.interesting.insert(0, b)

    def scan(self, group):

        a = GObject(blanc, self.radius, self.radius,
                    self.rect.centerx, self.rect.centery)

        pygame.gfxdraw.circle(State.screen, self.rect.centerx, self.rect.centery,
                              self.radius, (0,255,0,50))

        for x in group:
            if pygame.sprite.collide_circle(a, x):
                if x not in self.in_range:
                    self.in_range.append(x)
        a.kill()

    def scan_all(self):

        self.in_range.clear()
        for i in self.interesting:
            self.scan(i)

        # Is there anything interesting in range?
        try:
            if not self.locked.alive():
                self.locked = None
        except:
            self.locked = None

        if self.in_range:
            return True

    def lock_on(self):
        if self.in_range:
            self.locked = self.in_range[0]
            return True
        else:
            return False

    def auto_lock_on(self):
        #  Don't not switch target if it is still in range
        if self.locked != None:
            pass
        else:
            self.lock_on()

    def aim_locked(self):
        if self.locked != None:
            self.aim(self.locked)
