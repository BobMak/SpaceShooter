import threading
import time
import pygame as pg

from Ships import Ships as Sp
from Map import Maps
from Core import Events, Assets as A, State as St

clock = pg.time.Clock()


def main_loop():
    while True:
        if St.gamestate == "new_player":
            St.verse = Maps.Verse()
            St.window = Maps.Window(St.verse.sectors)
            print(St.window.current_sector)
            basic_ship = Sp.ShipGenerator.generate_test()
            St.window.addAvailable(basic_ship)
            St.window.focus = basic_ship
            St.graphics = Graphics()
            St.graphics_thread = threading.Thread(target=St.graphics.screen_redraw)
            St.graphics_thread.start()
            St.gamestate = "game"
        elif St.gamestate == "game":
            # Handle player input
            keys  = pg.key.get_pressed()
            m_left, m_middle, m_right = pg.mouse.get_pressed()
            # Getting in pause menu
            if keys[pg.K_ESCAPE]:  # and St.t[0]
                # To stop graphics thread
                pg.time.set_timer(pg.USEREVENT + 2, 10)
                # To unblock esc button
                pg.time.set_timer(pg.USEREVENT + 1, 300)
                St.paused = True
                while St.paused:
                    time.sleep(0.1)
            # camera control
            if keys[pg.K_c]:
                if St.window.focus:
                    St.window.move(St.window.focus.rect.centerx-St.window.width//2,
                                   St.window.focus.rect.centery-St.window.height//2)
            if keys[pg.K_w] or keys[pg.K_UP]:
                St.window.base_y += -1
            if keys[pg.K_s] or keys[pg.K_DOWN]:
                St.window.base_y += 1
            if keys[pg.K_a] or keys[pg.K_LEFT]:
                St.window.base_x += -1
            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                St.window.base_x += 1
            # Player module abilities
            if St.window.focus:
                for key in St.window.focus.controls.keys():
                    if isinstance(key, int) and keys[key]:
                        St.window.focus.controls[key]()
                    if m_right and "mouse_right" in St.window.focus.controls:
                        posx, posy = pg.mouse.get_pos()
                        posx += St.window.base_x
                        posy += St.window.base_y
                        St.window.focus.controls["mouse_right"](posx, posy)
            # Handle events
            for event in pg.event.get():
                if event.type in Events.eve:
                    e= Events.eve[event.type]
                    e[0](*e[1])
                    print('event {}({})'.format(e[0], e[1]))
            # Updates to object groups
            # Execute events that all objects are subscribed to
            for event in St.all_objects:
                event.run()
            # Sector updates
            for sector in St.window.sectors_on_screen:
                for obj in sector.updateable:
                    obj.update()
            # Every movable
            St.window.move_movable()
            # logic tick
            clock.tick(St.LOGIC_PER_SECOND)


class Graphics:
    def __init__(self):
        # Alive until player quits
        self.alive = True
        self.screen = pg.display.set_mode((St.window.width, St.window.height))

    def draw_rotating(self, obj):
        rect = obj.rotated_image.get_rect()
        rect.centerx = obj.rect.centerx - St.window.base_x
        rect.centery = obj.rect.centery - St.window.base_y
        self.screen.blit(obj.rotated_image_alpha, rect)

    def screen_redraw(self):
        while self.alive:
            self.screen_draw()
            pg.display.flip()
            clock.tick(St.FRAMES_PER_SECOND)

    def screen_draw(self):
        """Draws all game scene, does not flip."""
        for sector in St.window.sectors_on_screen:
            try:
                self.screen.blit(A.BG, (0, 0))
            except Exception as e:
                print("err: {}".format(e))
            for group in (sector.player_group, sector.visible, sector.effects):
                for obj in group:
                    try:
                        self.draw_rotating(obj)
                    except Exception as e:
                        print("** failed to draw {}:".format(obj), e)
            for object in sector.glow:
                object.update()
            for pl in sector.player_group:
                pl.show_HP()

