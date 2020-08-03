import pyglet as pg
import numpy as np
from numba import jit, cuda

from Core import Noise


screen = pg.window.Window(400, 400, )
conwey = None
pureNoise = np.zeros([400, 400])
active_regions = {}  # rects 40x40 (x, y)
BLK = 20


def update(x):
    screen.clear()
    conwey = Noise.getNoiseImage(size=400, persistance=0.5, depth=8)
    conwey.blit(0,0, width=400, height=400)


if __name__ == "__main__":
    pg.gl.glEnable(pg.gl.GL_BLEND)
    pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)

    pg.clock.schedule_interval(update, 1 / 60.0)
    pg.app.run()