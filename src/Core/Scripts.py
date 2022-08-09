import pickle
import random
import threading
import sys
import time

import pygame as pg

import Core.Assets as Assets
from Core.Asteroids import AdvAsteroid
from Core.Mechanics import Moving
from Entities.Player import Player
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


def main_loop(state):
    for x, y in enumerate(state.pl.turrets):
        y.number = x

    # terminate previous graphics thread if needed
    if state.graphics_thread:
        state.graphics.alive = False
        state.graphics_thread.join()
    state.graphics = Graphics(state)
    state.graphics_thread = threading.Thread(target=state.graphics.screen_redraw)
    state.graphics_thread.start()

    while state.state is not "quit":
        keys = pg.key.get_pressed()

        # Getting in pause menue
        if keys[pg.K_ESCAPE] and state.t[0]:  # and state.t[0]
            # To stop graphics thread
            pg.time.set_timer(pg.USEREVENT + 5, 10)
            # To unblock esc button
            pg.time.set_timer(pg.USEREVENT + 1, 300)
            state.t = (False, False, False, False)
            state.state = 'paused'

        if state.state == 'paused':
            time.sleep(0.5)
            continue
        elif state.state == 'exit':
            return

        # Perform player input
        for pl in state.player_group:
            for x in pl.arr_input:
                x(pl, keys)

        # everything else non-player input specific
        step(state)
        # logic tick
        state.clock.tick(state.LOGIC_PER_SECOND)


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


class Graphics:

    def __init__(self, state):
        # Alive until player quits
        self.alive = True
        self.state = state

    def screen_redraw(self):
        """
        Drwaing
        """
        while self.alive:
            screen_draw(self.state)
            pg.display.flip()
            self.state.clock.tick(self.state.FRAMES_PER_SECOND)

            if self.state.state== 'paused':
                pause_menu(self.state)
            if self.state.state== 'game_over':
                death_menu(self.state)
            if self.state.state == 'exit':
                self.alive = False


def pause_menu(state):
    print(state.t)
    W = state.W
    H = state.H
    bW = 200
    bH = 30
    bHd = 50

    temporary_bg = state.screen.copy()
    # Define button positions
    b_continue =  bt.B_Continue(  (W//2 - bW//2, H//3, bW, bH), state)
    b_startover = bt.B_Start_Over((W//2 - bW//2, H//3 + bHd, bW, bH), state)
    b_exit =      bt.B_Exit(      (W//2 - bW//2, H//3 + 2*bHd, bW, bH), state)
    menu = [b_continue, b_startover, b_exit]
    selection = 0
    menu[0].select()
    state.screen.blit(menu_BG, (0, 0))  # Draw a background

    while state.state == 'paused':

        screen_draw(state)

        for x in menu:
            state.screen.blit(x.image, x.rect)
            state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        pg.display.flip()

        for event in pg.event.get():
            # Propagate exit into main loop
            if event.type == pg.QUIT:
                state.state = 'exit'
                pg.event.post(pg.event.Event(pg.QUIT, {'QUIT': True}))
                sys.exit()

            keys = pg.key.get_pressed()

            if event.type == pg.USEREVENT + 1:
                state.t = (True, True, True, True)
                pg.time.set_timer(pg.USEREVENT + 1, 0)

            if (keys[pg.K_UP] or keys[pg.K_DOWN]) and state.t[0]:
                if keys[pg.K_UP]:
                    new_selection = max(0, selection -1)
                else:
                    new_selection = min(len(menu)-1, selection + 1)

                menu[selection].deselect()
                menu[new_selection].select()
                state.screen.blit(temporary_bg, (0, 0))
                state.screen.blit(menu_BG, (0, 0))
                for x in menu:
                    state.screen.blit(x.image, x.rect)
                    state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)
                selection = new_selection
                print(selection)
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
                menu[selection].action()


def death_menu(state):
    temporary_bg = state.screen.copy()
    b_exit = bt.B_Exit((Assets.WIDTH // 2 - 50, 320, 100, 30), state)
    b_startover = bt.B_Start_Over((Assets.WIDTH // 2 - 50, 200, 100, 30), state)
    menu = [b_startover, b_exit]
    selection = 0
    menu[0].select()
    state.screen.blit(menu_BG, (0, 0))  # draw dark background on previous
    # draw buttons
    for x in menu:
        state.screen.blit(x.image, x.rect)
        state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

    # remove player from screen
    state.player_group.empty()

    while (state.state == 'game_over'):
        Moving.move_movable(state)

        for i in state.time_dependent:
            if i.timer - i.time_count < 0:
                i.remove()
            else:
                i.time_count += 1

        screen_draw(state)

        for x in menu:
            state.screen.blit(x.image, x.rect)
            state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        pg.display.flip()

        for object in state.effects:
            object.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            keys = pg.key.get_pressed()

            if (keys[pg.K_UP] or keys[pg.K_DOWN]) and state.t[0]:
                if keys[pg.K_UP]:
                    new_selection = max(0, selection -1)
                else:
                    new_selection = min(len(menu)-1, selection + 1)

                menu[selection].deselect()
                menu[new_selection].select()
                state.screen.blit(temporary_bg, (0, 0))
                state.screen.blit(menu_BG, (0, 0))
                for x in menu:
                    state.screen.blit(x.image, x.rect)
                    state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)
                selection = new_selection
                print(selection)
                state.t = (False, False, False, False)
                pg.time.set_timer(pg.USEREVENT + 1, 100)

            if keys[pg.K_RETURN]:
                menu[selection].action()
                # state.t = (False, False, False, False)


def player_set(state):
    temporary_BG = pg.transform.scale(BG, [WIDTH, HEIGHT])
    state.screen.blit(temporary_BG, (0, 0))
    W = state.screen.get_width()
    H = state.screen.get_height()
    shiphighlights = []
    sh_width_padding = W // (len(State.ship_types.keys()) + 1)
    sh_width = 20
    for i, shipname in enumerate(State.ship_types.keys()):
        shiphighlights.append(bt.B_Ship_Highlihgts(
            (sh_width_padding + i*sh_width_padding - sh_width//2,
             sh_width,
             60,
             200),
            shipname,
            state
        ))
    menu = [
        shiphighlights,
        [
            bt.B_New_Game((W//2 - 150, H*2//3, 100, 30), state),
            bt.B_Exit((W//2 + 50, H*2//3, 100, 30), state)]
    ]
    selection = [0, 0]
    ship_selected = 0
    menu[0][0].select()

    menu_run = True

    # draw buttons and ship abilities

    while (menu_run):

        state.screen.blit(temporary_BG, (0, 0))
        for y in menu:
            for x in y:
                state.screen.blit(x.image, x.rect)

        for x in menu[1]:
            state.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        for i, line in enumerate(menu[0][ship_selected].text.split('\n')):
            state.screen.blit(pg.font.Font.render(menu[0][ship_selected].font,
                                                  line,
                                                  0, WHITE),
                              pg.Rect(W//2 -50, H//2 + i*20 - 50, 5, 5))

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            keys = pg.key.get_pressed()

            if keys[pg.K_UP]:

                if selection[0] > 0:

                    if selection[1] >= len(menu[selection[0]]) - 1:
                        menu[selection[0] - 1][len(menu[selection[0]]) - 1].select()
                        menu[selection[0]][selection[1]].deselect()
                        selection[1] = len(menu[selection[0]]) - 1

                    else:
                        menu[selection[0] - 1][selection[1]].select()
                        menu[selection[0]][selection[1]].deselect()

                    selection[0] += -1

                if selection[1] >= len(menu[selection[0]]):
                    selection[1] = len(menu[selection[0]]) - 1
                print(selection)

            if keys[pg.K_DOWN]:

                if selection[0] < len(menu) - 1:

                    if selection[1] >= len(menu[selection[0] + 1]) - 1:

                        menu[selection[0] + 1][len(menu[selection[0] + 1]) - 1].select()
                        menu[selection[0]][selection[1]].deselect()
                        selection[1] = len(menu[selection[0] + 1]) - 1

                    else:
                        menu[selection[0] + 1][selection[1]].select()
                        menu[selection[0]][selection[1]].deselect()
                    selection[0] += 1
                print(selection)

            if keys[pg.K_RIGHT]:

                if selection[1] < len(menu[selection[0]]) - 1:
                    menu[selection[0]][selection[1] + 1].select()
                    menu[selection[0]][selection[1]].deselect()
                    selection[1] += 1

                if selection[0] == 0:
                    ship_selected = selection[1]

            if keys[pg.K_LEFT]:

                if selection[1] > 0:
                    menu[selection[0]][selection[1] - 1].select()
                    menu[selection[0]][selection[1]].deselect()
                    selection[1] += -1

                if selection[0] == 0:
                    ship_selected = selection[1]

            if keys[pg.K_RETURN]:

                menu[selection[0]][selection[1]].action()

                if selection[0] == 1 and selection[1] == 0:
                    state.t = (False, False, False, False)
                    menu_run = False

