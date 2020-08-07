"""
Initial script
"""
import pyglet
from Core import State


if __name__ == "__main__":
    State.init()
    State.screen = pyglet.window.Window(800, 600)
    from Core.Scripts import main_loop
    pyglet.clock.schedule_interval(main_loop, 1 / 60.0)
    pyglet.app.run()
