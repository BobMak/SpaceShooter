import threading
import numpy as np
import time
import pygame as pg

import State as St
import Assets as A
import Funcs as F
import Events
import Buttons as bt

clock = pg.time.Clock()


def main_loop():
    St.graphics = Graphics()
    St.graphics_thread = threading.Thread(target=St.graphics.screen_redraw)
    St.graphics_thread.start()
    while True:
        # Handle player input
        keys = pg.key.get_pressed()
        # Getting in pause menu
        if keys[pg.K_ESCAPE]:  # and St.t[0]
            # To stop graphics thread
            pg.time.set_timer(pg.USEREVENT + 2, 10)
            # To unblock esc button
            pg.time.set_timer(pg.USEREVENT + 1, 300)
            St.t = (False, False, False, False)
            St.paused = True
            while St.paused:
                time.sleep(0.1)
        # Player module abilities
        for key in St.player.ship.controls.keys():
            if keys[key]:
                St.player.ship.controls[key]()
        # Handle events
        for event in pg.event.get():
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
        F.move_movable()
        # logic tick
        clock.tick(St.LOGIC_PER_SECOND)


class Graphics:
    def __init__(self):
        # Alive until player quits
        self.alive = True

    def screen_redraw(self):
        while self.alive:
            self.screen_draw()
            pg.display.flip()
            clock.tick(St.FRAMES_PER_SECOND)

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
                    F.draw_rotating(pl)
                except:
                    print("player faild to be drawn")
                speed = np.sqrt(pl.speed[0] ** 2 + pl.speed[1] ** 2)
                if speed > 8:
                    F.blur(pl, speed)

            for object in sector.glow:
                object.update()

            for object in sector.projectiles:
                try:
                    F.draw_rotating(object)
                    F.blur(object, object.speed_max)
                except:
                    print("projectile fails to be drawn")

            for object in sector.effects:
                F.draw_rotating(object)

            for object in St.window.interface:
                St.screen.blit(object.image, object.rect)

            for pl in sector.player_group:
                pl.show_HP()

