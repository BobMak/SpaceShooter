import pygame
from Assets import *
from Buttons import *
from ShipParams import *

from Scripts import *

def pause_menu():

    global t
    print(t)

    temporary_BG = screen.copy()
    b_continue  =   B_Continue((200, 200, 100, 30))
    b_startover = B_Start_Over((200, 250, 100, 30))
    b_exit      =       B_Exit((200, 300, 100, 30))
    menu = [b_continue, b_startover, b_exit]
    selection = 0
    menu[0].select()
    screen.blit(menu_BG, (0,0))     #draw dark background on previous

    menu_run = True
    #draw buttons

    while(menu_run):

        screen_draw()

        for x in menu:
            screen.blit(x.image, x.rect)

            screen.blit(pygame.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            keys = pygame.key.get_pressed()

            if event.type == pygame.USEREVENT+1:
                global t
                for x in range(len(t)):
                    t[x] = True
                pygame.time.set_timer(pygame.USEREVENT+1, 0)

            if keys[pygame.K_UP]:

                if selection > 0:

                    menu[selection-1].select()
                    menu[selection].deselect()
                    selection += -1
                    screen.blit(temporary_BG, (0,0))
                    screen.blit(menu_BG, (0,0))
                    for x in menu:
                        screen.blit(x.image, x.rect)
                        screen.blit(pygame.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

            if keys[pygame.K_DOWN]:

                if selection < len(menu) -1:

                    menu[selection+1].select()
                    menu[selection].deselect()
                    selection += 1
                    screen.blit(temporary_BG, (0,0))
                    screen.blit(menu_BG, (0,0))
                    for x in menu:
                        screen.blit(x.image, x.rect)
                        screen.blit(pygame.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

            if keys[pygame.K_RETURN]:

                menu[selection].action()
                if selection == 0:
                    menu_run = False
                    t[0] = False
                    pygame.time.set_timer(pygame.USEREVENT+1, 300)

            if keys[pygame.K_ESCAPE]:
                if (t[0] == True):
                    menu_run = False
                    t[0] = False
                    pygame.time.set_timer(pygame.USEREVENT+1, 300)
                else:
                    pygame.time.set_timer(pygame.USEREVENT+1, 0)
                    pygame.time.set_timer(pygame.USEREVENT+1, 300)


    return threading.Thread(target =screen_redraw)

def main_menu():

        #####   declare menu buttons    #####
    temporary_BG = pygame.image.load('C:/vova/github/SpaceShooter/assets/animations/Background/BG_2_n_res.png')
    screen.blit(temporary_BG, (0,0))
    b_new_game = B_New_Game((180, 200, 100, 30))
    b_stats = B_Stats((180, 250, 100, 30))
    b_exit = B_Exit((180, 300, 100, 30))
    menu = [b_new_game, b_stats, b_exit]
    selection = 0
    menu[0].select()

    global menu_run
    menu_run = False

    #draw buttons
    for x in menu:
        screen.blit(x.image, x.rect)

        screen.blit(pygame.font.Font.render(x.font, x.text, 0, WHITE), x.rect)
    while(menu_run):

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:

                if selection > 0:

                    menu[selection-1].select()
                    menu[selection].deselect()
                    selection += -1
                    screen.blit(temporary_BG, (0,0))
                    for x in menu:
                        screen.blit(x.image, x.rect)
                        screen.blit(pygame.font.Font.render(x.font, x.text,
                                                            0, WHITE),
                                    x.rect)

            if keys[pygame.K_DOWN]:

                if selection < len(menu) -1:

                    menu[selection+1].select()
                    menu[selection].deselect()
                    selection += 1
                    screen.blit(temporary_BG, (0,0))
                    for x in menu:
                        screen.blit(x.image, x.rect)
                        screen.blit(pygame.font.Font.render(x.font, x.text,
                                                            0, WHITE),
                                    x.rect)

            if keys[pygame.K_RETURN]:

                menu[selection].action()
                if selection == 0:
                    global menu_ru
                    menu_run = False
                    print("st")


def death_menu():

    global t

    temporary_BG = screen.copy()
    b_exit = B_Exit((200, 320, 100, 30))
    b_startover = B_Start_Over((200, 200, 100, 30))
    menu = [b_startover, b_exit]
    selection = 0
    menu[0].select()
    screen.blit(menu_BG, (0,0))     #draw dark background on previous
    #draw buttons
    for x in menu:
        screen.blit(x.image, x.rect)

        screen.blit(pygame.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

    while(True):
        move_movable()

        for x in asteroids:
            bound_pass(x)

        for x in projectiles:
            bound_pass(x)

        for i in time_dependent:
            if i.timer - i.time_count < 0:
                i.remove()
            else:
                i.time_count +=1

        screen_draw()

        for x in menu:
            screen.blit(x.image, x.rect)

            screen.blit(pygame.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        pygame.display.flip()

        for object in effects:
            object.update()

        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:

                if selection > 0:

                    menu[selection-1].select()
                    menu[selection].deselect()
                    selection += -1
                    screen.blit(temporary_BG, (0,0))
                    screen.blit(menu_BG, (0,0))
                    for x in menu:
                        screen.blit(x.image, x.rect)
                        screen.blit(pygame.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

            if keys[pygame.K_DOWN]:

                if selection < len(menu) -1:

                    menu[selection+1].select()
                    menu[selection].deselect()
                    selection += 1
                    screen.blit(temporary_BG, (0,0))
                    screen.blit(menu_BG, (0,0))
                    for x in menu:
                        screen.blit(x.image, x.rect)
                        screen.blit(pygame.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

            if keys[pygame.K_RETURN]:

                menu[selection].action()
                t[0] = False
    return None

def player_set():

    temporary_BG = pygame.image.load('C:/vova/Background/BG_13.png')
    temporary_BG = pygame.transform.scale(temporary_BG, [width, height])
    screen.blit(temporary_BG, (0,0))
    b_new_game = B_New_Game((140, 400, 100, 30))
    ship_highlights_1 = B_Ship_Highlihgts((30, 20, 60, 200), 0)
    ship_highlights_2 = B_Ship_Highlihgts((100, 20, 60, 200), 1)
    ship_highlights_3 = B_Ship_Highlihgts((170, 20, 60, 200), 2)
    b_exit = B_Exit((250, 400, 100, 30))
    menu = [[ship_highlights_1, ship_highlights_2, ship_highlights_3], [b_new_game, b_exit]]
    selection = [0,0]
    menu[0][0].select()

    menu_run = True

    #draw buttons
    for x in menu:
        for y in x:
            screen.blit(y.image, y.rect)

            screen.blit(pygame.font.Font.render(y.font, y.text, 0, WHITE), y.rect)
    while(menu_run):

        screen.blit(temporary_BG, (0,0))
        for y in menu:
            for x in y:
                screen.blit(x.image, x.rect)
                screen.blit(pygame.font.Font.render(x.font, x.text, 0, WHITE), x.rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:

                if selection[0] > 0:

                    if selection[1] >= len(menu[selection[0]])-1:
                        menu[selection[0]-1][len(menu[selection[0]])-1].select()
                        menu[selection[0]][selection[1]].deselect()
                        selection[1] = len(menu[selection[0]])-1

                    else:
                        menu[selection[0]-1][selection[1]].select()
                        menu[selection[0]][selection[1]].deselect()

                    selection[0] += -1

                if selection[1] >= len(menu[selection[0]]):
                    selection[1] = len(menu[selection[0]])-1
                print(selection)

            if keys[pygame.K_DOWN]:

                if selection[0] < len(menu) -1:

                    if selection[1] >=  len(menu[selection[0]+1])-1:

                        menu[selection[0]+1][len(menu[selection[0]+1])-1].select()
                        menu[selection[0]][selection[1]].deselect()
                        selection[1] = len(menu[selection[0]+1])-1

                    else:
                        menu[selection[0]+1][selection[1]].select()
                        menu[selection[0]][selection[1]].deselect()
                    selection[0] += 1
                print(selection)

            if keys[pygame.K_RIGHT]:

                if selection[1] < len(menu[selection[0]]) -1 :

                    menu[selection[0]][selection[1]+1].select()
                    menu[selection[0]][selection[1]].deselect()
                    selection[1] += 1
                print(selection)

            if keys[pygame.K_LEFT]:

                if selection[1] > 0:

                    menu[selection[0]][selection[1]-1].select()
                    menu[selection[0]][selection[1]].deselect()
                    selection[1] += -1
                print(selection)

            if keys[pygame.K_RETURN]:

                menu[selection[0]][selection[1]].action()
                if selection[0] == 1 and selection[1] == 0:
                    t[0] = False
                    print("breaking")
                    menu_run = False
