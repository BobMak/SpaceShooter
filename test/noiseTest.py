import pyglet as pg
import numpy as np
from numba import jit, cuda

from Core import Noise


screen = pg.window.Window(400, 400, )
conwey = None
box = None
ang = 0
pureNoise = np.zeros([400, 400])
active_regions = {}  # rects 40x40 (x, y)
BLK = 20


def update(x):
    global conwey, ang
    screen.clear()
    # ang += 1
    conwey = Noise.getNoiseImage(rgba=[1, 0.9, 0.5, 0.2], size=400, persistance=0.9, depth=16)
    conwey.anchor_x = 200
    conwey.anchor_y = 200
    box = pg.sprite.Sprite(conwey, x=200, y=200)
    box.draw()
    # conwey = Noise.getNoiseImage(rgba=[0.1, 0.9, 0.1, 0.2], size=400, persistance=0.9, depth=32)
    # conwey.anchor_x = 200
    # conwey.anchor_y = 200
    # box = pg.sprite.Sprite(conwey, x=200, y=200)
    # box.draw()


if __name__ == "__main__":
    pg.gl.glEnable(pg.gl.GL_BLEND)
    pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)

    pg.clock.schedule_interval(update, 1)
    conwey = Noise.getNoiseImage(size=400, persistance=1, depth=32)
    conwey.anchor_x = 200
    conwey.anchor_y = 200
    box = pg.sprite.Sprite(conwey, x=200, y=200)
    pg.app.run()