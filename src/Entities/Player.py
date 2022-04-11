import pickle
import threading

import pygame
import pygame.gfxdraw as gfx

from Core import Controls, Assets, State
from Core.Mechanics import Animation
from Ships.Ship import Ship


class Player(Ship):
    def __init__(self, img, x, y, lives, **kwargs):
        super().__init__(img, x, y, **kwargs)
        self.ships = []
        self.add(self.state.player_group)
        self.lives = lives

    def destroy(self):
        self.lives += -1
        if self.lives > 0:
            threading.Timer(1, self.state.spawn_player).start()
        else:
            # graphics thread termination call
            # pygame.time.set_timer(pygame.USEREVENT+5, 1000)
            threading.Timer(1, self.state.game_over).start()

        super().destroy()

    def show_HP(self):
        for i in range(self.lives):
            self.state.screen.blit(Assets.live, (270 + 35 * (1 + i), 20, 30, 30))

        gfx.box(self.state.screen,
                (10, 10, self.hp * 100 / self.max_hp, 20), (0, 255, 0, 50))

    def show_acceleration_reserve(self):
        gfx.box(self.state.screen,
                (10, 30, self.acceleration_reserve * 100 / self.max_acceleration_reserve, 20),
                (255, 255, 0, 50))

    def show_missiles(self):
        for x in range(self.missiles):
            gfx.box(self.state.screen, (10 + x * 10, 50, 9, 10), (255, 0, 0, 50))

    def draw_rotating(self):
        super().draw_rotating()
        # HUD
        self.show_HP()
        self.show_acceleration_reserve()
        self.show_missiles()

    @staticmethod
    def ship_assign(picked_ship, lives, state, x=None, y=None):
        '''Assign all properties to given ship. Usually when creating new instance
        of ship'''
        if not x or not y:
            x = state.W / 2
            y = state.H / 2
        ship = Player(State.ship_types[picked_ship]["image"],
                      x, y,
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
                      mass=State.ship_types[picked_ship]['mass'],
                      state=state)

        for a in State.ship_types[picked_ship]['controls']:
            ship.arr_input.append(Controls.controls[a])

        ship.addMissiles(State.ship_types[picked_ship]['missiles'])
        msl_type = State.ship_types[picked_ship]['missile']
        Animation.prepareExplosions(State.missile_types[msl_type]['expl_params'], state)
        blt_type = State.ship_types[picked_ship]['bolt']
        Animation.prepareExplosions(State.projectile_types[blt_type]["expl_params"], state)

        if state.pl:
            state.pl.kill()
        state.pl = ship

        return ship

