import threading
import sys
import time
import pygame as pg
import State as St, Assets as A, Funcs as F
import Events
import Buttons as bt

import Classes

clock = pg.time.Clock()


def main_loop(player):
    St.graphics = Graphics()
    St.graphics_thread = threading.Thread(target=St.graphics.screen_redraw)
    St.graphics_thread.start()
    while True:
        # Handle player input
        keys = pygame.key.get_pressed()
        # Getting in pause menu
        if keys[pygame.K_ESCAPE]:  # and St.t[0]
            # To stop graphics thread
            pygame.time.set_timer(pygame.USEREVENT + 2, 10)
            # To unblock esc button
            pygame.time.set_timer(pygame.USEREVENT + 1, 300)
            St.t = (False, False, False, False)
            St.paused = True
            while St.paused:
                time.sleep(0.1)
        if keys[pygame.K_e]:  # and St.t[0]
            # To stop graphics thread
            pygame.time.set_timer(pygame.USEREVENT + 3, 10)
            # To unblock esc button
            time.sleep(0.1)
        # Player module abilities
        for key in player.ship.controls.keys():
            if keys[key]:
                player.ship.controls[key]()
        # Handle events
        for event in pygame.event.get():
            try:
                e=Events.eve[event]
                e[0](*e[1])
            except Exception as e:
                print('unhandled event', e)
        # Updates to object groups
        # Execute events that all objects are subscribed to
        for event in St.all_objects:
            event.run()
        # Every movable
        move_movable()
        # logic tick
        clock.tick(St.LOGIC_PER_SECOND)


class Graphics:
    def __init__(self):
        # Alive until player quits
        self.alive = True

    def screen_redraw(self):
        while self.alive:
            self.screen_draw()
            pygame.display.flip()
            clock.tick(St.FRAMES_PER_SECOND)
            if St.paused:
                pause_menu()

    def screen_draw(self):
        """Draws all game scene, does not flip."""
        for sector in St.window.sectors_on_screen:
            for object in sector.effects:
                object.update()
            try:
                St.screen.blit(A.BG, (0, 0))
            except Exception as e:
                print("err: {}".format(e))

            for pl in sector.player_group:
                try:
                    draw_rotating(pl)
                except:
                    print("player faild to be drawn")
                speed = np.sqrt(pl.speed[0] ** 2 + pl.speed[1] ** 2)
                if speed > 8:
                    blur(pl, speed)

            for object in St.window.interface:
                St.screen.blit(object.image, object.rect)


def pause_menu():
    print(St.t)
    temporary_bg = St.screen.copy()
    # Define button positions
    b_continue = bt.BContinue((200, 200, 100, 30))
    b_startover = bt.BStartOver((200, 250, 100, 30))
    b_exit = bt.BExit((200, 300, 100, 30))
    menu = [b_continue, b_startover, b_exit]
    selection = 0
    menu[0].select()
    St.screen.blit(menu_BG, (0, 0))  # Draw a background
    while St.paused:
        St.graphics.screen_draw()
        for x in menu:
            St.screen.blit(x.image, x.rect)
            St.screen.blit(pg.font.Font.render(x.font, x.text, 0, (255,255,255)), x.rect)
        pg.display.flip()
        for event in pg.event.get():
            # Propagate exit into main loop
            if event.type == pg.QUIT:
                St.paused = False
                pg.event.post(pg.event.Event(pg.QUIT, {'QUIT': True}))
            keys = pg.key.get_pressed()
            if event.type == pg.USEREVENT + 1:
                St.t = (True, True, True, True)
                pg.time.set_timer(pg.USEREVENT + 1, 0)

            if keys[pg.K_UP]:
                if selection > 0:
                    menu[selection - 1].select()
                    menu[selection].deselect()
                    selection += -1
                    St.screen.blit(temporary_bg, (0, 0))
                    St.screen.blit(menu_BG, (0, 0))
                    for x in menu:
                        St.screen.blit(x.image, x.rect)
                        St.screen.blit(pg.font.Font.render(x.font, x.text, 0, St.WHITE), x.rect)

            if keys[pg.K_DOWN]:
                if selection < len(menu) - 1:
                    menu[selection + 1].select()
                    menu[selection].deselect()
                    selection += 1
                    St.screen.blit(temporary_bg, (0, 0))
                    St.screen.blit(menu_BG, (0, 0))
                    for x in menu:
                        St.screen.blit(x.image, x.rect)
                        St.screen.blit(pg.font.Font.render(x.font, x.text, 0, St.WHITE), x.rect)

            if keys[pg.K_RETURN]:
                menu[selection].action()
                if selection == 0:
                    St.paused = False
                    St.t = (False, False, False, False)
                    pg.time.set_timer(pg.USEREVENT + 1, 300)

            if keys[pg.K_ESCAPE]:
                if St.t[0] == True:
                    St.paused = False
                    St.t = (False, False, False, False)
                    pg.time.set_timer(pg.USEREVENT + 1, 300)
                else:
                    pg.time.set_timer(pg.USEREVENT + 1, 0)
                    pg.time.set_timer(pg.USEREVENT + 1, 300)


def death_menu():
    temporary_BG = St.screen.copy()
    b_exit = bt.BExit((200, 320, 100, 30))
    b_startover = bt.BStartOver((200, 200, 100, 30))
    menu = [b_startover, b_exit]
    selection = 0
    menu[0].select()
    St.screen.blit(menu_BG, (0, 0))  # draw dark background on previous
    # draw buttons
    for x in menu:
        St.screen.blit(x.image, x.rect)
        St.screen.blit(pg.font.Font.render(x.font, x.text, 0, St.WHITE), x.rect)

    while (True):
        move_movable()
        St.window.screen_draw()
        for x in menu:
            St.screen.blit(x.image, x.rect)
            St.screen.blit(pg.font.Font.render(x.font, x.text, 0, St.WHITE), x.rect)
        pg.display.flip()
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
                    St.screen.blit(temporary_BG, (0, 0))
                    St.screen.blit(menu_BG, (0, 0))
                    for x in menu:
                        St.screen.blit(x.image, x.rect)
                        St.screen.blit(pg.font.Font.render(x.font, x.text, 0, St.WHITE), x.rect)

            if keys[pg.K_DOWN]:
                if selection < len(menu) - 1:
                    menu[selection + 1].select()
                    menu[selection].deselect()
                    selection += 1
                    St.screen.blit(temporary_BG, (0, 0))
                    St.screen.blit(menu_BG, (0, 0))
                    for x in menu:
                        St.screen.blit(x.image, x.rect)
                        St.screen.blit(pg.font.Font.render(x.font, x.text, 0, St.WHITE), x.rect)

            if keys[pg.K_RETURN]:
                menu[selection].action()
                St.t = (False, False, False, False)


def player_set():
    temporary_BG = pg.image.load(os.path.join("..", "assets", "BG_12.png"))
    temporary_BG = pg.transform.scale(temporary_BG, [St.WIDTH, St.HEIGHT])
    St.screen.blit(temporary_BG, (0, 0))
    b_new_game = bt.BNewGame((140, 400, 100, 30))
    ship_highlights_1 = bt.BShipHighlihgts((30, 20, 60, 200), 0)
    ship_highlights_2 = bt.BShipHighlihgts((100, 20, 60, 200), 1)
    ship_highlights_3 = bt.BShipHighlihgts((170, 20, 60, 200), 2)
    b_exit = bt.BExit((250, 400, 100, 30))
    menu = [[ship_highlights_1, ship_highlights_2, ship_highlights_3], [b_new_game, b_exit]]
    selection = [0, 0]
    ship_selected = 0
    menu[0][0].select()
    menu_run = True
    # draw buttons
    for x in menu:
        for y in x:
            St.screen.blit(y.image, y.rect)
            St.screen.blit(pg.font.Font.render(menu[0][ship_selected].font, y.text, 0, St.WHITE),
                              pg.Rect(300, 200, 5, 5))

    while (menu_run):
        St.screen.blit(temporary_BG, (0, 0))
        for y in menu:
            for x in y:
                St.screen.blit(x.image, x.rect)
        for x in menu[1]:
            St.screen.blit(pg.font.Font.render(x.font, x.text, 0, St.WHITE), x.rect)

        St.screen.blit(pg.font.Font.render(menu[0][ship_selected].font,
                                              menu[0][ship_selected].text,
                                              0, St.WHITE),
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
                print(selection)

            if keys[pg.K_LEFT]:
                if selection[1] > 0:
                    menu[selection[0]][selection[1] - 1].select()
                    menu[selection[0]][selection[1]].deselect()
                    selection[1] += -1
                if selection[0] == 0:
                    ship_selected = selection[1]
                print(selection)

            if keys[pg.K_RETURN]:
                menu[selection[0]][selection[1]].action()
                if selection[0] == 1 and selection[1] == 0:
                    St.t = (False, False, False, False)
                    print("breaking")
                    menu_run = False
