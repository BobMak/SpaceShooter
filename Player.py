import pickle

import Controls
from Mechanics import *
import Scripts

import pygame.gfxdraw as gfx

from Projectile import Projectile


class Player(GObject, Moving, Vulnerable):
    '''Player(image, x, y, lives, bolt=0,
              complex_sh=-1, width=None, height=None)'''
    bolt = 0
    arr_input = []
    player_hull_group = pygame.sprite.Group()
    shields_orbit_group = pygame.sprite.Group()
    shields = pygame.sprite.Group()
    turrets = pygame.sprite.Group()
    orbiting = pygame.sprite.Group()
    mounts = []

    hull_group_ang = 0

    space_lock = False
    special_lock = False
    missile_lock = False
    shield_lock = False
    acceleration_lock = False
    locks = [space_lock, special_lock, missile_lock, shield_lock, acceleration_lock]

    def __init__(self, image, x, y, lives, bolt=0,
                 complex_sh=-1, player=True, width=None, height=None):

        self.MAX_HP = 10
        self.MAX_S_HP = 10
        self.ROTATION = 10
        self.ACCELERATION = 1
        self.DEACCELERATION = 0.5
        self.ENV_DEACCELERATION = 0.25
        self.MAX_ACCELERATION_RESERVE = 8.0
        self.ACCELERATION_RESERVE_REGENERATION = 0.07
        self.ACCELERATION_RATE = 0.2

        self.acceleration_reserve = copy.deepcopy(self.MAX_ACCELERATION_RESERVE)
        self.hp = copy.deepcopy(self.MAX_HP)
        self.shield_hp = copy.deepcopy(self.MAX_S_HP)
        self.speed = [0,0]
        self.lives = lives
        super().__init__(image, x, y, width=width, height=height)
        Moving.__init__(self)
        Vulnerable.__init__(self, State.SHIP_HP[complex_sh])
        """#################FIX HP###################"""

        if player == True:

            self.add(State.player_group)

            for i in range(lives):
                r = GObject(live, 270 + 35 * (1 + i), 20, 30, 30)
                r.add(State.interface)
                State.movable.remove(r)

            for x in State.complex_rects[complex_sh]:
                b = Colliding(x[0], x[1], x[2], x[3], self)
                self.player_hull_group.add(b)

        self.bolt = bolt
        self.missiles = 0

        self.time_count_fire = 0
        self.timer_fire = State.prj_cooldown[bolt]

        self.time_count_special = 0
        self.timer_special = State.spec_cooldown[complex_sh]

        self.time_count_missile = 0
        self.timer_missile = State.prj_cooldown[State.n_bolts + bolt]

        self.time_count_shield = 0
        self.timer_shield = 50

        self.time_count_acceleration = 0
        self.timer_acceleration = 50

        self.counts = [self.time_count_fire, self.time_count_special,
                       self.time_count_missile, self.time_count_shield]

        self.timers = [self.timer_fire, self.timer_special,
                       self.timer_missile, self.timer_shield]

        self.distance = 0
        self.orbit_ang = 0
        self.player = player

    def addMissiles(self, number):
        self.missiles += number

    def destroy(self):

        self.kill()
        self.rotate(0)
        self.speed = [0,0]
        Animation.FX_explosion(self.rect.centerx, self.rect.centery)

        for x in self.shields:
            x.down()

        if self.player == True:

            for x in self.mounts:
                x.kill()
            for x in self.shields:
                x.kill()
            for x in self.player_hull_group:
                x.kill()
            self.lives += -1

            if self.lives > -1:
                pygame.time.set_timer(pygame.USEREVENT+2, 500)
            else:
                # graphics thread termination call
                pygame.time.set_timer(pygame.USEREVENT+5, 10)
                with open('save.pkl', 'wb') as f:
                    pickle.dump(State.save, f, pickle.HIGHEST_PROTOCOL)

                Scripts.death_menu()

    def damage(self, dmg):

        self.hp += -max(0, dmg)
        if self.hp < 0:
            self.destroy()
            if self.player == True:
                return True

    def show_HP(self):
        gfx.box(State.screen,
                (10, 10, self.hp * 100 / self.MAX_HP, 20), (0, 255, 0, 50))

    def show_acceleration_reserve(self):
        gfx.box(State.screen,
                (10, 30, self.acceleration_reserve * 100 / self.MAX_ACCELERATION_RESERVE, 20),
                (255, 255, 0, 50))

    def show_missiles(self):
        for x in range(self.missiles):
            gfx.box(State.screen, (10 + x * 10, 50, 9, 10), (255, 0, 0, 50))

    def m_add(self, mounted):
        self.mounts.append(mounted)

    def sh_add(self, shield):
        self.shields.add(shield)

    def scan(self):
        min_dist = State.asteroids.sprites[0]

        for i in State.asteroids:
            dist = np.sqrt((self.rect.x - i.rect.x)**2
                         + (self.rect.y - i.rect.y)**2)
            if dist < min_dist:
                min_dist = dist

        return min_dist

    def fire(self):
        if self.locks[0] == False:
            self.locks[0] = True
            Projectile.shot(self, self.look_dir, self.bolt)

    def accelerate(self, temp):
        if not self.acceleration_reserve < 0.4:
            self.acceleration_reserve = max(0.0, self.acceleration_reserve - self.ACCELERATION_RATE)
            super()._accelerate(temp)
        else:
            self.acceleration_lock = True

    def update(self):
        self.acceleration_reserve = min(self.MAX_ACCELERATION_RESERVE,
                                        self.ACCELERATION_RESERVE_REGENERATION + self.acceleration_reserve)

        for n in range(len(self.locks)):
            if self.locks[n]:
                self.counts[n] += 1
                if self.timers[n] < self.counts[n]:
                    self.counts[n] = 0
                    self.locks[n] = False

    @staticmethod
    def ship_assign(picked_ship, lives, player):
        '''Assign all properties to given ship. Usually when creating new instance
        of ship'''
        ship = Player(Assets.SHIPS_IMGS[picked_ship],
                      Assets.HEIGHT // 2, Assets.HEIGHT // 2,
                      complex_sh=picked_ship - 1, bolt=picked_ship,
                      lives=lives, width=None, height=None, player=player)
        ship.rotate(0)
        ship.arr_input = Controls.ABILITIES[picked_ship]

        ship.ROTATION = State.SHIP_CONSTANTS[picked_ship][0]
        ship.ACCELERATION = State.SHIP_CONSTANTS[picked_ship][1]
        ship.DEACCELERATION = State.SHIP_CONSTANTS[picked_ship][2]
        ship.ENV_DEACCELERATION = State.SHIP_CONSTANTS[picked_ship][3]
        ship.hp = State.SHIP_CONSTANTS[picked_ship][4]
        ship.shield_hp = State.SHIP_CONSTANTS[picked_ship][5]
        ship.type = State.SHIP_CONSTANTS[picked_ship][6]
        ship.addMissiles(State.SHIP_CONSTANTS[picked_ship][7])

        return ship
