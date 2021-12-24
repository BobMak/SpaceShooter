from Mechanics import *
from Projectile import Projectile
from Turret import Turret
import Funcs


class AutoTurret(Turret):
    mode = 2
    def __init__(self, image, radius, mounted_on, bolt_id, cooldown,
                 groups = None, distance = 20, look_dir = 0,
                 width = 20, height = 20, restriction = None):
        """
        Turret shoting prjoectiles with predictions of aim's
        position by its speed.
        'prj_speed' defines speed of projectiles.
        'cooldown' - in seconds.
        'bolt_numer' - index of given bolt in bolts' lists
        """

        super().__init__(image, radius, mounted_on, groups, distance,
                         look_dir, width, height, restriction)

        self.bolt_id = bolt_id
        self.bolt_img = State.projectile_types[bolt_id]['image']
        self.prj_speed = State.projectile_types[bolt_id]['speed']

        self.predict_pos = GObject(ball_img, 1, 1, -50, 1)
        self.blocked = False
        self.timer = cooldown * State.FPS
        self.time_count = 0
        self.add(mounted_on.turrets)

        mounted_on.m_add(self)

    def get_predict_pos(self):

        self.predict_pos.rect = copy.copy(self.locked.rect)
        length = np.sqrt((self.rect.x - self.locked.rect.x)**2
                          + (self.rect.y - self.locked.rect.y)**2)

        try:
            if (self.prj_speed*np.cos(np.deg2rad(self.look_dir))) != -99:
                self.predict_pos.rect.centerx += (round(self.locked.speed[0]
                                                       *length/self.prj_speed)
                                                        *(1/self.prj_speed + 1))

        except:
            pass

        try:
            if (self.prj_speed*np.sin(np.deg2rad(self.look_dir))) != -99:
                self.predict_pos.rect.centery += (round(self.locked.speed[1]
                                                       *length/self.prj_speed)
                                                        *(1/self.prj_speed + 1))

        except:
            pass

        if self.blocked:
            self.time_count += 1

            if self.time_count > self.timer:
                self.time_count = 0
                self.blocked = False

    def aim_locked(self):

        if self.locked != None:
            if self.aim(self.predict_pos) and not self.blocked:

                self.blocked = True
                Projectile.shot(self, self.look_dir, self.bolt_id)

    def auto_fire(self):

        self.scan_all()
        self.auto_lock_on()
        try:
            self.get_predict_pos()
        except:
            pass
        self.aim_locked()

    def closest(self):
        if self.scan_all():
            self.locked = self.in_range[0]
            dist = (abs(self.in_range[0].rect.x - self.mounted_on.rect.x)
                  + abs(self.in_range[0].rect.y - self.mounted_on.rect.y))

            for x in self.in_range:
                t = (abs(x.rect.x - self.rect.x) + abs(x.rect.y - self.rect.y))
                if t < dist:
                    dist = t
                    self.locked = x
            try:
                self.get_predict_pos()
            except:
                pass
            self.aim_locked()

    def hunt(self):
        try:
            if self.locked == None or not self.locked.alive():
                self.scan_all()
                self.lock_on()
            else:
                pass

        except:
            pass
            self.lock_on()

        try:
            #self.aim(self.locked)
            if self.locked in self.in_range:

                self.get_predict_pos()
                self.aim_locked()
        except:
            pass

    mods = [auto_fire, closest, hunt]

    def switch_aim(self):
        if len(self.in_range) > 1:
            try:
                self.locked = self.in_range[self.in_range.index(self.locked)+1]
            except:
                self.locked = self.in_range[self.in_range.index(self.locked)-1]

        else:
            pass

    def active(self):
        self.mods[self.mode](self)

