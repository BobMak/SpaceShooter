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
    ang += 1
    if ang > 359:
        ang = 0
    box.rotation = ang
    box.draw()


if __name__ == "__main__":
    pg.gl.glEnable(pg.gl.GL_BLEND)
    pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)

    pg.clock.schedule_interval(update, 1 / 60.0)
    conwey = Noise.getNoiseImage(size=400, persistance=0.5, depth=8)
    conwey.anchor_x = 200
    conwey.anchor_y = 200
    box = pg.sprite.Sprite(conwey, x=200, y=200)
    pg.app.run()