import random
import threading
import sys

import pygame as pg

import Core.Assets as Assets
from Core.Asteroids import AdvAsteroid
from Core.Mechanics import Moving
import Core.State as State
from Utils import orbit_eliptic, orbit_rotate

from UI import Buttons as bt
from Core.Assets import *


def spawn_wave(state, wave_config=None):
    if wave_config is None:
        wave_config = State.waves[state.level]
    for _ in range(wave_config["number"]):
        if random.choice([True, False]):
            proX = random.choice([random.randint(-20,0),
                                  random.randint(Assets.WIDTH, Assets.WIDTH + 20)])
            proY = random.randint(-20, Assets.HEIGHT + 20)
        else:
            proX = random.randint(-20, Assets.WIDTH + 20)
            proY = random.choice([random.randint(-20,0),
                                  random.randint(Assets.HEIGHT, Assets.HEIGHT + 20)])

        AdvAsteroid(wave_config, proX, proY, 4, (0.0, 0.0), state=state, init_speed=wave_config['init_speed'])

    state.level += 1
    state.wave_spawning = False
    state.state = 'game'


def main_loop(state):
    main_menu = MainMenu(state)
    pause_menu = PauseMenu(state)
    death_menu = DeathMenu(state)
    old_state = ''

    while state.state is not "quit":
        if state.state is not old_state:
            print(f"state: {state.state}")
            old_state = state.state

        keys = pg.key.get_pressed()

        # Getting in pause menue
        if keys[pg.K_ESCAPE] and state.t[0]:  # and state.t[0]
            # To stop graphics thread
            pg.time.set_timer(pg.USEREVENT + 5, 10)
            # To unblock esc button
            pg.time.set_timer(pg.USEREVENT + 1, 300)
            state.t = (False, False, False, False)
            # re-init pause menu to capture current screen
            pause_menu = PauseMenu(state)
            state.state = 'paused'
        if state.state == 'paused':
            pause_menu()
        elif state.state == 'game_over':
            step(state)
            screen_draw(state)
            death_menu()
        elif state.state == 'game':
            # Perform player input
            for pl in state.player_group:
                for x in pl.arr_input:
                    x(pl, keys)
            # everything else non-player input specific
            step(state)
            screen_draw(state)
        elif state.state == 'new_game':
            state.reset()
            state.spawn_player()
            spawn_wave(state)
            state.state = 'game'
        elif state.state == 'next_wave':
            spawn_wave(state)
        elif state.state == 'menu':
            main_menu()

        state.clock.tick(state.LOGIC_PER_SECOND)
        pg.display.flip()
    print("quitting")
    pg.event.post(pg.event.Event(pg.QUIT, {'QUIT': True}))
    pg.quit()

def terminate_graphics(state):
    state.graphics.alive = False
    state.graphics_thread.join()


def step(state, events=True):
    if events:
        # Handle in-game events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                threading.Timer(0.5, terminate_graphics, [state]).start()
                sys.exit()

            # Release all key locks
            if event.type == pg.USEREVENT + 1:
                state.t = (True, True, True, True)
                pg.time.set_timer(pg.USEREVENT + 1, 0)

    # Updates to object groups
    #
    # Execute events that all objects are subscribed to
    for event in state.all_objects:
        event.run()

    Moving.move_movable(state)

    for m in state.script_mob_group:
        try:
            m.update()
        except:
            pass

    for pl in state.player_group:

        for x in pl.hull_group:
            orbit_rotate(x.source, x, 0, x.distance, x.angle)

        for x in pl.shields:
            x.update()

        for x in pl.orbiting:
            orbit_eliptic(pl, x)

    for z in state.missiles:
        z.update()
        z.rect.move(z.v)

    ##########      Logic       #########

    for y in state.asteroids:
        for x in state.hit_waves:
            if pg.sprite.collide_circle(x, y):
                x.damage(y.hp)
                if y.damage(x.hp, moving=x):
                    break
        for x in state.pl.shields:
            if pg.sprite.collide_circle(y, x):
                x.damage(4, moving=y)
                if y.damage(5, moving=x):
                    break
        for i in state.projectiles:
            if pg.sprite.collide_circle(y, i):
                i.damage(y)
        for i in state.missiles:
            if pg.sprite.collide_circle(y, i):
                i.blow_up()
        if y not in state.noclip_asteroids:
            for pl in state.player_group:
                for i in pl.hull_group:
                    if pg.sprite.collide_circle(y, i):
                        pl.damage(y.hp)
                        if y.damage(2, moving=pl):
                            break

    for pl in state.player_group:
        pl.update()
        for i in pl.shields:
            i.rect.move(i.v)

        for x in pl.turrets:
            x.auto_fire()

        for x in pl.orbiting:
            x.active()

        for x in state.pickupables:
            if pg.sprite.collide_circle(pl, x):
                x.pickup(pl)

    for i in state.time_dependent:
        if i.timer < i.time_count:
            i.kill()
        else:
            i.update()
            i.time_count += 1

    if len(state.asteroids) == 0 and not state.wave_spawning:
        print('spawning...')
        threading.Timer(3, spawn_wave, args=[state]).start()
        state.wave_spawning = True


def screen_draw(state):
    """
    Draws all game scene, does not flip.
    """
    # drawing related state updates
    for group in [
        state.noclip_asteroids,
        state.effects
    ]:
        for object in group:
            try:
                object.update()
            except:
                pass
    # background
    try:
        state.screen.blit(BG, (0, 0))
    except Exception as e:
        print("err: {}".format(e))
    # drawing
    for group in [
        state.asteroids,
        state.noclip_asteroids,
        state.script_mob_group,
        state.projectiles,
        state.missiles,
        state.effects,
        state.glow,
        state.player_group
    ]:
        for object in group:
            try:
                object.draw_rotating()
            except:
                print("failed to draw")
    # special drawing
    for object in state.interface:
        state.screen.blit(object.image, object.rect)


class PauseMenu:
    def __init__(self, state):
        self.state = state
        print(state.t)
        W = state.W
        H = state.H
        bW = 200
        bH = 30
        bHd = 50

        self.temporary_bg = state.screen.copy()
        # Define button positions
        b_continue =  bt.B_Continue(  (W//2 - bW//2, H//3, bW, bH), state)
        b_startover = bt.B_Start_Over((W//2 - bW//2, H//3 + bHd, bW, bH), state)
        b_exit =      bt.B_Exit(      (W//2 - bW//2, H//3 + 2*bHd, bW, bH), state)
        menu = [b_continue, b_startover, b_exit]
        self.selection = 0
        menu[0].select()
        self.menu = menu
        state.screen.blit(menu_BG, (0, 0))  # Draw a background

    def __call__(self, *args, **kwargs):
        state = self.state
        # screen_draw(state)
        for x in self.menu:
            state.screen.blit(x.image, x.rect)
            state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        for event in pg.event.get():
            # Propagate exit into main loop
            if event.type == pg.QUIT:
                state.state = 'quit'
                pg.event.post(pg.event.Event(pg.QUIT, {'QUIT': True}))
                sys.exit()

            keys = pg.key.get_pressed()

            if event.type == pg.USEREVENT + 1:
                state.t = (True, True, True, True)
                pg.time.set_timer(pg.USEREVENT + 1, 0)

            if (keys[pg.K_UP] or keys[pg.K_DOWN]) and state.t[0]:
                if keys[pg.K_UP]:
                    new_selection = max(0, self.selection -1)
                else:
                    new_selection = min(len(self.menu)-1, self.selection + 1)

                self.menu[self.selection].deselect()
                self.menu[new_selection].select()
                state.screen.blit(self.temporary_bg, (0, 0))
                state.screen.blit(menu_BG, (0, 0))
                for x in self.menu:
                    state.screen.blit(x.image, x.rect)
                    state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)
                self.selection = new_selection
                print(self.selection)
                state.t = (False, False, False, False)
                pg.time.set_timer(pg.USEREVENT + 1, 100)

            if keys[pg.K_ESCAPE]:
                if state.t[0] == True:
                    state.state = 'game_playing'
                    state.t = (False, False, False, False)
                    pg.time.set_timer(pg.USEREVENT + 1, 100)
                else:
                    pg.time.set_timer(pg.USEREVENT + 1, 0)
                    pg.time.set_timer(pg.USEREVENT + 1, 100)

            if keys[pg.K_RETURN]:
                self.menu[self.selection].action()


class DeathMenu:
    def __init__(self, state):
        self.state = state
        self.temporary_bg = state.screen.copy()
        b_exit = bt.B_Exit((Assets.WIDTH // 2 - 50, 320, 100, 30), state)
        b_startover = bt.B_Start_Over((Assets.WIDTH // 2 - 50, 200, 100, 30), state)
        menu = [b_startover, b_exit]
        self.selection = 0
        menu[0].select()
        self.menu = menu
        state.screen.blit(menu_BG, (0, 0))  # draw dark background on previous
        # draw buttons
        for x in menu:
            state.screen.blit(x.image, x.rect)
            state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        # remove player from screen
        state.player_group.empty()

    def __call__(self):
        for i in self.state.time_dependent:
            if i.timer - i.time_count < 0:
                i.remove()
            else:
                i.time_count += 1

        for x in self.menu:
            self.state.screen.blit(x.image, x.rect)
            self.state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        for object in self.state.effects:
            object.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            keys = pg.key.get_pressed()

            if (keys[pg.K_UP] or keys[pg.K_DOWN]) and self.state.t[0]:
                if keys[pg.K_UP]:
                    new_selection = max(0, self.selection -1)
                else:
                    new_selection = min(len(self.menu)-1, self.selection + 1)

                self.menu[self.selection].deselect()
                self.menu[new_selection].select()
                self.state.screen.blit(self.temporary_bg, (0, 0))
                self.state.screen.blit(menu_BG, (0, 0))
                for x in self.menu:
                    self.state.screen.blit(x.image, x.rect)
                    self.state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)
                self.selection = new_selection
                self.state.t = (False, False, False, False)
                pg.time.set_timer(pg.USEREVENT + 1, 100)

            if keys[pg.K_RETURN]:
                self.menu[self.selection].action()
                # self.state.t = (False, False, False, False)

class MainMenu:
    def __init__(self, state):
        self.state = state
        self.temporary_BG = pg.transform.scale(BG, [WIDTH, HEIGHT])
        state.screen.blit(self.temporary_BG, (0, 0))
        self.W = state.screen.get_width()
        self.H = state.screen.get_height()
        shiphighlights = []
        sh_width_padding = self.W // (len(State.ship_types.keys()) + 1)
        sh_width = 20
        for i, shipname in enumerate(State.ship_types.keys()):
            shiphighlights.append(bt.B_Ship_Highlihgts(
                (sh_width_padding + i * sh_width_padding - sh_width // 2,
                 sh_width,
                 60,
                 200),
                shipname,
                state
            ))
        menu = [
            shiphighlights,
            [
                bt.B_New_Game((self.W // 2 - 150, self.H * 2 // 3, 100, 30), state),
                bt.B_Exit((self.W // 2 + 50, self.H * 2 // 3, 100, 30), state)]
        ]
        self.selection = [0, 0]
        self.ship_selected = 0
        menu[0][0].select()
        self.menu = menu
        self.menu_run = True

    def __call__(self):
        self.state.screen.blit(self.temporary_BG, (0, 0))
        for y in self.menu:
            for x in y:
                self.state.screen.blit(x.image, x.rect)

        for x in self.menu[1]:
            self.state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        for i, line in enumerate(self.menu[0][self.ship_selected].text.split('\n')):
            self.state.screen.blit(pg.font.Font.render(self.menu[0][self.ship_selected].font,
                                                  line,
                                                  0, WHITE),
                              pg.Rect(self.W//2 -50, self.H//2 + i*20 - 50, 5, 5))

        # pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            keys = pg.key.get_pressed()

            if keys[pg.K_UP]:

                if self.selection[0] > 0:

                    if self.selection[1] >= len(self.menu[self.selection[0]]) - 1:
                        self.menu[self.selection[0] - 1][len(self.menu[self.selection[0]]) - 1].select()
                        self.menu[self.selection[0]][self.selection[1]].deselect()
                        self.selection[1] = len(self.menu[self.selection[0]]) - 1

                    else:
                        self.menu[self.selection[0] - 1][self.selection[1]].select()
                        self.menu[self.selection[0]][self.selection[1]].deselect()

                    self.selection[0] += -1

                if self.selection[1] >= len(self.menu[self.selection[0]]):
                    self.selection[1] = len(self.menu[self.selection[0]]) - 1
                print(self.selection)

            if keys[pg.K_DOWN]:

                if self.selection[0] < len(self.menu) - 1:

                    if self.selection[1] >= len(self.menu[self.selection[0] + 1]) - 1:

                        self.menu[self.selection[0] + 1][len(self.menu[self.selection[0] + 1]) - 1].select()
                        self.menu[self.selection[0]][self.selection[1]].deselect()
                        self.selection[1] = len(self.menu[self.selection[0] + 1]) - 1

                    else:
                        self.menu[self.selection[0] + 1][self.selection[1]].select()
                        self.menu[self.selection[0]][self.selection[1]].deselect()
                    self.selection[0] += 1
                print(self.selection)

            if keys[pg.K_RIGHT]:

                if self.selection[1] < len(self.menu[self.selection[0]]) - 1:
                    self.menu[self.selection[0]][self.selection[1] + 1].select()
                    self.menu[self.selection[0]][self.selection[1]].deselect()
                    self.selection[1] += 1

                if self.selection[0] == 0:
                    self.ship_selected = self.selection[1]

            if keys[pg.K_LEFT]:

                if self.selection[1] > 0:
                    self.menu[self.selection[0]][self.selection[1] - 1].select()
                    self.menu[self.selection[0]][self.selection[1]].deselect()
                    self.selection[1] += -1

                if self.selection[0] == 0:
                    self.ship_selected = self.selection[1]

            if keys[pg.K_RETURN]:

                self.menu[self.selection[0]][self.selection[1]].action()

                if self.selection[0] == 1 and self.selection[1] == 0:
                    self.state.t = (False, False, False, False)
                    self.menu_run = False

