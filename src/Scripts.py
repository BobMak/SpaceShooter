import threading
import sys
import time

from src.Classes import *
from src.State import *
from src.Funcs import *
import Events
from src import Buttons as bt

clock = pygame.time.Clock()


def main_loop(realGuy):
    pl = realGuy
    for x, y in enumerate(pl.turrets):
        y.number = x

    State.graphics = Graphics()
    State.graphics_thread = threading.Thread(target=State.graphics.screen_redraw)
    State.graphics_thread.start()

    while True:
        # Handle player input
        keys = pygame.key.get_pressed()
        # Getting in pause menu
        if keys[pygame.K_ESCAPE]:  # and State.t[0]
            # To stop graphics thread
            pygame.time.set_timer(pygame.USEREVENT + 2, 10)
            # To unblock esc button
            pygame.time.set_timer(pygame.USEREVENT + 1, 300)
            State.t = (False, False, False, False)
            State.paused = True
            while State.paused:
                time.sleep(0.1)
        # Player module abilities
        for key in realGuy.ship.controls.keys():
            if keys[key]:
                realGuy.ship.controls[key]()

        # Handle events
        for event in pygame.event.get():
            try:
                Events.eve[event]
            except Exception as e:
                print('unhandled event', e)

        # Updates to object groups
        # Execute events that all objects are subscribed to
        for event in State.all_objects:
            event.run()
        # Perform player input
        for pl in player_group:
            for x in pl.arr_input:
                x(pl, keys)
            bound_pass(pl)

        # Every movable
        move_movable()

        # Collisions
        for x in hit_waves:
            for y in asteroids:
                if pygame.sprite.collide_circle(x, y):
                    y.damage(x.hp)
                    x.damage(y.hp)

        player_group.update()
        # logic tick
        clock.tick(LOGIC_PER_SECOND)


def screen_draw():
    """
    Draws all game scene, does not flip.
    """
    for object in effects:
        object.update()
    try:
        State.screen.blit(BG, (0, 0))
    except Exception as e:
        print("err: {}".format(e))

    for pl in player_group:
        try:
            draw_rotating(pl)
        except:
            print("player faild to be drawn")
        speed = np.sqrt(pl.speed[0] ** 2 + pl.speed[1] ** 2)
        if speed > 8:
            blur(pl, speed)

    for object in glow:
        object.update()

    for object in projectiles:
        try:
            draw_rotating(object)
            blur(object, object.speed_max)
        except:
            print("projectile fails to be drawn")

    for object in effects:
        draw_rotating(object)

    for object in interface:
        State.screen.blit(object.image, object.rect)

    for pl in player_group:
        pl.show_HP()


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
            pygame.display.flip()
            clock.tick(FRAMES_PER_SECOND)

            if State.paused:
                pause_menu()


def pause_menu():
    print(State.t)

    temporary_bg = State.screen.copy()
    # Define button positions
    b_continue = bt.BContinue((200, 200, 100, 30))
    b_startover = bt.BStartOver((200, 250, 100, 30))
    b_exit = bt.BExit((200, 300, 100, 30))
    menu = [b_continue, b_startover, b_exit]
    selection = 0
    menu[0].select()
    State.screen.blit(menu_BG, (0, 0))  # Draw a background

    while State.paused:

        screen_draw()

        for x in menu:
            State.screen.blit(x.image, x.rect)

            State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        pg.display.flip()

        for event in pg.event.get():
            # Propagate exit into main loop
            if event.type == pg.QUIT:
                State.paused = False
                pg.event.post(pg.event.Event(pg.QUIT, {'QUIT': True}))
            keys = pg.key.get_pressed()

            if event.type == pg.USEREVENT + 1:
                State.t = (True, True, True, True)
                pg.time.set_timer(pg.USEREVENT + 1, 0)

            if keys[pg.K_UP]:

                if selection > 0:

                    menu[selection - 1].select()
                    menu[selection].deselect()
                    selection += -1
                    State.screen.blit(temporary_bg, (0, 0))
                    State.screen.blit(menu_BG, (0, 0))
                    for x in menu:
                        State.screen.blit(x.image, x.rect)
                        State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

            if keys[pg.K_DOWN]:

                if selection < len(menu) - 1:

                    menu[selection + 1].select()
                    menu[selection].deselect()
                    selection += 1
                    State.screen.blit(temporary_bg, (0, 0))
                    State.screen.blit(menu_BG, (0, 0))
                    for x in menu:
                        State.screen.blit(x.image, x.rect)
                        State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

            if keys[pg.K_RETURN]:

                menu[selection].action()
                if selection == 0:
                    State.paused = False
                    State.t = (False, False, False, False)
                    pg.time.set_timer(pg.USEREVENT + 1, 300)

            if keys[pg.K_ESCAPE]:
                if State.t[0] == True:
                    State.paused = False
                    State.t = (False, False, False, False)
                    pg.time.set_timer(pg.USEREVENT + 1, 300)
                else:
                    pg.time.set_timer(pg.USEREVENT + 1, 0)
                    pg.time.set_timer(pg.USEREVENT + 1, 300)


def death_menu():
    temporary_BG = State.screen.copy()
    b_exit = bt.BExit((200, 320, 100, 30))
    b_startover = bt.BStartOver((200, 200, 100, 30))
    menu = [b_startover, b_exit]
    selection = 0
    menu[0].select()
    State.screen.blit(menu_BG, (0, 0))  # draw dark background on previous
    # draw buttons
    for x in menu:
        State.screen.blit(x.image, x.rect)

        State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

    while (True):
        move_movable()

        for x in asteroids:
            bound_pass(x)

        for x in projectiles:
            bound_pass(x)

        for i in time_dependent:
            if i.timer - i.time_count < 0:
                i.remove()
            else:
                i.time_count += 1

        screen_draw()

        for x in menu:
            State.screen.blit(x.image, x.rect)

            State.screen.blit(pg.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        pg.display.flip()

        for object in effects:
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
    temporary_BG = pg.image.load(os.path.join("..", "assets", "BG_12.png"))
    temporary_BG = pg.transform.scale(temporary_BG, [WIDTH, HEIGHT])
    State.screen.blit(temporary_BG, (0, 0))
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
                    State.t = (False, False, False, False)
                    print("breaking")
                    menu_run = False