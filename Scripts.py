import random
import threading
import sys
import time

import pygame as pg

import Assets
from Asteroids import AdvAsteroid
from Mechanics import Moving
from Player import Player
import State
from Utils import orbit_eliptic, orbit_rotate

import Buttons as bt
from Assets import *

clock = pg.time.Clock()


def spawn_wave():
    level = State.level
    for _ in range(State.waves[level]["number"]):
        if random.choice([True, False]):
            proX = random.choice([random.randint(-20,0),
                                  random.randint(Assets.WIDTH, Assets.WIDTH+20)])
            proY = random.randint(-20, Assets.HEIGHT+20)
        else:
            proX = random.randint(-20, Assets.WIDTH+20)
            proY = random.choice([random.randint(-20,0),
                                  random.randint(Assets.HEIGHT, Assets.HEIGHT+20)])

        x = AdvAsteroid(level+1, proX, proY, 4, [0, 0])

    State.level += 1


def main_loop():
    for x, y in enumerate(State.pl.turrets):
        y.number = x

    # terminate previous graphics thread if needed
    if State.graphics_thread:
        State.graphics.alive = False
        State.graphics_thread.join()
    State.graphics = Graphics()
    State.graphics_thread = threading.Thread(target=State.graphics.screen_redraw)
    State.graphics_thread.start()

    while State.state is not "quit":
        keys = pg.key.get_pressed()

        # Getting in pause menue
        if keys[pg.K_ESCAPE] and State.t[0]:  # and State.t[0]
            # To stop graphics thread
            pg.time.set_timer(pg.USEREVENT + 5, 10)
            # To unblock esc button
            pg.time.set_timer(pg.USEREVENT + 1, 300)
            State.t = (False, False, False, False)
            State.state = 'paused'

        if State.state == 'paused':
            time.sleep(0.5)
            continue
        elif State.state == 'exit':
            return

        # Handle in-game events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                State.graphics.alive = False
                sys.exit()

            # Release all key locks
            if event.type == pg.USEREVENT + 1:
                State.t = (True, True, True, True)
                pg.time.set_timer(pg.USEREVENT + 1, 0)

            # Spawn player if no asteroid in range. Called after player's death
            if event.type == pg.USEREVENT + 2:

                pg.time.set_timer(pg.USEREVENT + 2, 0)

                buff_sp = pg.sprite.Sprite()
                buff_sp.rect = menu_button.get_rect()
                buff_sp.rect.width = 100
                buff_sp.rect.height = 100
                buff_sp.rect.centerx = Assets.WIDTH / 2
                buff_sp.rect.centery = Assets.HEIGHT / 2
                if len(pg.sprite.spritecollide(buff_sp, State.asteroids, 0)) == 0:
                    State.interface.empty()
                    State.pl = Player.ship_assign(State.picked_ship, State.pl.lives)
                # Do not spawn player if there are State.asteroids around, and wait 100 milliseconds instead
                else:
                    pg.time.set_timer(pg.USEREVENT + 2, 100)

            # Spawn wave
            if event.type == pg.USEREVENT + 3:
                spawn_wave()
                State.wave_spawning = False
                pg.time.set_timer(pg.USEREVENT + 3, 0)

            # handle game over
            if event.type == pg.USEREVENT + 4:
                State.state = "game_over"
                pg.time.set_timer(pg.USEREVENT + 4, 0)

        # Updates to object groups
        #
        # Execute events that all objects are subscribed to
        for event in State.all_objects:
            event.run()
        # Perform player input
        for pl in State.player_group:
            for x in pl.arr_input:
                x(pl, keys)
            #
            pl.bound_pass()

        Moving.move_movable()

        for x in State.asteroids:
            x.bound_pass()

        for m in State.script_mob_group:
            m.bound_pass()

            try:
                m.update()
            except:
                pass

        for pl in State.player_group:

            pl.bound_pass()

            for x in pl.hull_group:
                orbit_rotate(x.source, x, 0, x.distance, x.angle)
                x.bound_pass()

            for x in pl.turrets:
                x.bound_pass()

            for x in pl.shields:
                x.rect.centerx = x.source.rect.centerx
                x.rect.centery = x.source.rect.centery

            for x in pl.orbiting:
                x.bound_pass()
                orbit_eliptic(pl, x)

        for x in State.projectiles:
            x.bound_pass()

        for z in State.missiles:
            z.bound_pass()
            z.update()
            z.rect.move(z.v)

        for x in State.mob_group:
            x.bound_pass()

        ##########      Logic       #########

        for y in State.asteroids:
            for x in State.hit_waves:
                if pg.sprite.collide_circle(x, y):
                    x.damage(y.hp)
                    if y.damage(x.hp, moving=x):
                        break
            for x in pl.shields:
                if pg.sprite.collide_circle(y, x):
                    x.damage(4)
                    if y.damage(5, moving=x):
                        break
            for i in State.projectiles:
                if pg.sprite.collide_circle(y, i):
                    i.damage(y)
            for i in State.missiles:
                if pg.sprite.collide_circle(y, i):
                    i.blow_up()
            if y not in State.noclip_asteroids:
                for pl in State.player_group:
                    for i in pl.hull_group:
                        if pg.sprite.collide_circle(y, i):
                            pl.damage(y.hp)
                            if y.damage(2, moving=pl):
                                break

        for pl in State.player_group:
            pl.update()
            for i in pl.shields:
                i.rect.move(i.v)

            for x in pl.turrets:
                x.auto_fire()

            for x in pl.orbiting:
                x.active()

            for x in State.pickupables:
                if pg.sprite.collide_circle(pl, x):
                    x.pickup(pl)

        for i in State.time_dependent:
            if i.timer < i.time_count:
                i.kill()
            else:
                i.time_count += 1

        if len(State.asteroids) == 0 and not State.wave_spawning:
            print('spawning...')
            pg.time.set_timer(pg.USEREVENT + 3, 2000)
            State.wave_spawning = True

        # logic tick
        clock.tick(State.LOGIC_PER_SECOND)


def screen_draw():
    """
    Draws all game scene, does not flip.
    """
    # drawing related state updates
    for group in [
        State.noclip_asteroids,
        State.effects
    ]:
        for object in group:
            try:
                object.update()
            except:
                pass
    # background
    try:
        State.screen.blit(BG, (0, 0))
    except Exception as e:
        print("err: {}".format(e))
    # drawing
    for group in [
        State.asteroids,
        State.noclip_asteroids,
        State.script_mob_group,
        State.projectiles,
        State.missiles,
        State.effects,
        State.glow,
        State.player_group
    ]:
        for object in group:
            try:
                object.draw_rotating()
            except:
                print("failed to draw")
    # special drawing
    for object in State.interface:
        State.screen.blit(object.image, object.rect)


class Graphics:

    def __init__(self):
        # Alive until player quits
        self.alive = True

    def screen_redraw(self):
        """
        Drwaing
        """
        while self.alive:
            screen_draw()
            pg.display.flip()
            clock.tick(State.FRAMES_PER_SECOND)

            if State.state=='paused':
                pause_menu()
            if State.state=='game_over':
                death_menu()
            if State.state == 'exit':
                self.alive = False


def pause_menu():
    print(State.t)

    temporary_bg = State.screen.copy()
    # Define button positions
    b_continue = bt.B_Continue((200, 200, 100, 30))
    b_startover = bt.B_Start_Over((200, 250, 100, 30))
    b_exit = bt.B_Exit((200, 300, 100, 30))
    menu = [b_continue, b_startover, b_exit]
    selection = 0
    menu[0].select()
    State.screen.blit(menu_BG, (0, 0))  # Draw a background

    while State.state=='paused':

        screen_draw()

        for x in menu:
            State.screen.blit(x.image, x.rect)
            State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        pg.display.flip()

        for event in pg.event.get():
            # Propagate exit into main loop
            if event.type == pg.QUIT:
                State.state = 'exit'
                pg.event.post(pg.event.Event(pg.QUIT, {'QUIT': True}))
                sys.exit()

            keys = pg.key.get_pressed()

            if event.type == pg.USEREVENT + 1:
                State.t = (True, True, True, True)
                pg.time.set_timer(pg.USEREVENT + 1, 0)

            if keys[pg.K_UP] and State.t[0]:
                new_selection = max(0, selection -1)
                menu[selection].deselect()
                menu[new_selection].select()
                State.screen.blit(temporary_bg, (0, 0))
                State.screen.blit(menu_BG, (0, 0))
                for x in menu:
                    State.screen.blit(x.image, x.rect)
                    State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)
                selection = new_selection
                print(selection)
                State.t = (False, False, False, False)
                pg.time.set_timer(pg.USEREVENT + 1, 300)

            if keys[pg.K_DOWN] and State.t[0]:
                new_selection = min(len(menu)-1, selection + 1)
                menu[selection].deselect()
                menu[new_selection].select()
                State.screen.blit(temporary_bg, (0, 0))
                State.screen.blit(menu_BG, (0, 0))
                for x in menu:
                    State.screen.blit(x.image, x.rect)
                    State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)
                selection = new_selection
                print(selection)
                State.t = (False, False, False, False)
                pg.time.set_timer(pg.USEREVENT + 1, 300)

            if keys[pg.K_ESCAPE]:
                if State.t[0] == True:
                    State.state = 'game_playing'
                    State.t = (False, False, False, False)
                    pg.time.set_timer(pg.USEREVENT + 1, 300)
                else:
                    pg.time.set_timer(pg.USEREVENT + 1, 0)
                    pg.time.set_timer(pg.USEREVENT + 1, 300)

            if keys[pg.K_RETURN]:
                menu[selection].action()


def death_menu():
    temporary_BG = State.screen.copy()
    b_exit = bt.B_Exit((Assets.WIDTH//2 - 50, 320, 100, 30))
    b_startover = bt.B_Start_Over((Assets.WIDTH//2 - 50, 200, 100, 30))
    menu = [b_startover, b_exit]
    selection = 0
    menu[0].select()
    State.screen.blit(menu_BG, (0, 0))  # draw dark background on previous
    # draw buttons
    for x in menu:
        State.screen.blit(x.image, x.rect)
        State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

    # remove player from screen
    State.player_group.empty()

    while (State.state == 'game_over'):
        Moving.move_movable()

        for x in State.asteroids:
            x.bound_pass()

        for x in State.projectiles:
            x.bound_pass()

        for i in State.time_dependent:
            if i.timer - i.time_count < 0:
                i.remove()
            else:
                i.time_count += 1

        # screen_draw()

        for x in menu:
            State.screen.blit(x.image, x.rect)
            State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        pg.display.flip()

        for object in State.effects:
            object.update()

        clock.tick(30)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            keys = pg.key.get_pressed()

            if keys[pg.K_UP]:

                if selection > 0:

                    menu[selection - 1].select()
                    menu[selection].deselect()
                    selection += -1
                    State.screen.blit(temporary_BG, (0, 0))
                    State.screen.blit(menu_BG, (0, 0))
                    for x in menu:
                        State.screen.blit(x.image, x.rect)
                        State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

            if keys[pg.K_DOWN]:

                if selection < len(menu) - 1:

                    menu[selection + 1].select()
                    menu[selection].deselect()
                    selection += 1
                    State.screen.blit(temporary_BG, (0, 0))
                    State.screen.blit(menu_BG, (0, 0))
                    for x in menu:
                        State.screen.blit(x.image, x.rect)
                        State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

            if keys[pg.K_RETURN]:
                menu[selection].action()
                State.t = (False, False, False, False)


def player_set():
    temporary_BG = pg.image.load(os.path.join("assets", "BG_12.png"))
    temporary_BG = pg.transform.scale(temporary_BG, [WIDTH, HEIGHT])
    State.screen.blit(temporary_BG, (0, 0))
    menu = [
        [
            bt.B_Ship_Highlihgts((30, 20, 60, 200), 'tick'),
            bt.B_Ship_Highlihgts((100, 20, 60, 200), 'hippo'),
            bt.B_Ship_Highlihgts((170, 20, 60, 200), 'wolf'),
            bt.B_Ship_Highlihgts((240, 20, 60, 200), 'generated')],
        [
            bt.B_New_Game((140, 400, 100, 30)),
            bt.B_Exit((250, 400, 100, 30))]
    ]
    selection = [0, 0]
    ship_selected = 0
    menu[0][0].select()

    menu_run = True

    # draw buttons

    for x in menu:
        for y in x:
            State.screen.blit(y.image, y.rect)
            State.screen.blit(pg.font.Font.render(menu[0][ship_selected].font, y.text, 0, WHITE),
                              pg.Rect(300, 200, 5, 5))

    while (menu_run):

        State.screen.blit(temporary_BG, (0, 0))
        for y in menu:
            for x in y:
                State.screen.blit(x.image, x.rect)

        for x in menu[1]:
            State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        State.screen.blit(pg.font.Font.render(menu[0][ship_selected].font,
                                              menu[0][ship_selected].text,
                                              0, WHITE),
                          pg.Rect(300, 200, 5, 5))

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
                    State.t = (False, False, False, False)
                    menu_run = False

