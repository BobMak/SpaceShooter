import pickle

import pygame
import pygame.gfxdraw as gfx

from Core import Controls, Assets, State
from Core.Mechanics import Animation
from Ships.Ship import Ship


class Player(Ship):
    def __init__(self, img, x, y, lives, **kwargs):
        super().__init__(img, x, y, **kwargs)
        self.ships = []

        self.add(State.player_group)

        self.lives = lives

    def destroy(self):
        super().destroy()

        self.lives += -1

        if self.lives > -1:
            pygame.time.set_timer(pygame.USEREVENT+2, 500)
        else:
            # graphics thread termination call
            pygame.time.set_timer(pygame.USEREVENT+5, 1000)
            with open('../../save.pkl', 'wb') as f:
                pickle.dump(State.save, f, pickle.HIGHEST_PROTOCOL)

            pygame.time.set_timer(pygame.USEREVENT + 4, 1000)

    def show_HP(self):
        for i in range(self.lives):
            State.screen.blit(Assets.live, (270 + 35 * (1 + i), 20, 30, 30))

        gfx.box(State.screen,
                (10, 10, self.hp * 100 / self.max_hp, 20), (0, 255, 0, 50))

    def show_acceleration_reserve(self):
        gfx.box(State.screen,
                (10, 30, self.acceleration_reserve * 100 / self.max_acceleration_reserve, 20),
                (255, 255, 0, 50))

    def show_missiles(self):
        for x in range(self.missiles):
            gfx.box(State.screen, (10 + x * 10, 50, 9, 10), (255, 0, 0, 50))

    def draw_rotating(self):
        super().draw_rotating()
        # HUD
        self.show_HP()
        self.show_acceleration_reserve()
        self.show_missiles()

    @staticmethod
    def ship_assign(picked_ship, lives):
        '''Assign all properties to given ship. Usually when creating new instance
        of ship'''

        ship = Player(State.ship_types[picked_ship]["image"],
                      Assets.HEIGHT // 2, Assets.HEIGHT // 2,
                      complex_sh=State.ship_types[picked_ship]['hit_box'],
                      lives=lives,
                      bolt=State.ship_types[picked_ship]['bolt'],
                      missile=State.ship_types[picked_ship]['missile'],
                      hp=State.ship_types[picked_ship]['hull'],
                      shield=State.ship_types[picked_ship]['shields'],
                      rotation_rate=State.ship_types[picked_ship]['rotation_rate'],
                      acceleration=State.ship_types[picked_ship]['acceleration'],
                      max_acceleration_reserve=State.ship_types[picked_ship]['acceleration_tank'],
                      acceleration_burn_rate=State.ship_types[picked_ship]['acceleration_burn_rate'],
                      acceleration_reserve_regeneration=State.ship_types[picked_ship][
                        'acceleration_reserve_regeneration'],
                      deacceleration=State.ship_types[picked_ship]['deacceleration'],
                      env_friction=State.ship_types[picked_ship]['env_deacceleration'],
                      width=None, height=None,
                      mass=State.ship_types[picked_ship]['mass'])

        for a in State.ship_types[picked_ship]['controls']:
            ship.arr_input.append(Controls.controls[a])

        ship.addMissiles(State.ship_types[picked_ship]['missiles'])
        msl_type = State.ship_types[picked_ship]['missile']
        Animation.prepareExplosions(**State.missile_types[msl_type]['expl_params'])
        blt_type = State.ship_types[picked_ship]['bolt']
        Animation.prepareExplosions(**State.projectile_types[blt_type]["expl_params"])

        return ship

