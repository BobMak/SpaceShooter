"""
Initial script
"""
import pyglet
from Core import State


if __name__ == "__main__":
    State.init()
    State.width, State.height = 800, 600
    State.screen = pyglet.window.Window(State.width, State.height)
    from Core.Scripts import main_loop
    pyglet.clock.schedule_interval(main_loop, 1 / 60.0)
    pyglet.app.run()
