import threading
import time
import pyglet as pg

from Ships import Ships as Sp
from Map import Maps
from Core import Events, Assets as A, State as St


def main_loop(u):
    keys = pg.window.key.KeyStateHandler()
    if St.gamestate == "new_player":
        St.verse = Maps.Verse()
        St.window = Maps.Window(St.verse.sectors, St.width, St.height)
        player = Sp.ShipFactory.generate_test()
        St.window.addAvailable(player)
        St.window.focus = player
        St.gamestate = "game"
    elif St.gamestate == "game":
        # Sector updates
        for sector in St.window.sectors_on_screen:
            for obj in sector.updateable:
                obj.update()
        Graphics.screen_redraw()
        if St.window.focus:
            St.window.followFocus()
    elif St.gamestate == "pause":
        time.sleep(1)
        if keys[pg.window.key.ESCAPE]:
            St.gamestate = "game"


@St.screen.event
def on_mouse_motion(x, y, dx, dy):
    aim = St.window.focus.get_aim_dir((x + St.window.base_x, y + St.window.base_y, 1, 1))
    St.window.focus.set_rotation(aim - 180)
@St.screen.event
def on_mouse_press(x, y, button, modifiers):
    pass
@St.screen.event
def on_mouse_release(x, y, button, modifiers):
    pass
@St.screen.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    pass
@St.screen.event
def on_key_press(symbol, modifiers):
    # Getting in pause menu
    if symbol==pg.window.key.ESCAPE:
        St.gamestate = "pause"
    # Control of focused object
    if St.window.focus:
        St.window.focus.add_update(St.window.focus.controls[symbol])
@St.screen.event
def on_key_release(symbol, modifiers):
    # Control of focused object
    if St.window.focus:
        St.window.focus.remove_update(St.window.focus.controls[symbol])


class Graphics:
    @staticmethod
    def screen_redraw():
        St.screen.clear()
        St.window.draw()
        for sector in St.window.sectors_on_screen:
            for obj in sector.all_objects:
                obj.draw()

