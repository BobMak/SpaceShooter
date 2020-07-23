import random
import time
import pyglet as pg
import numpy as np


screen = pg.window.Window(400, 400, )
pg.resource.path = ["../assets"]
pg.resource.reindex()
asteroid = pg.resource.image("asteroid.png")
astr = pg.sprite.Sprite(asteroid, 100, 100)
lable = pg.text.Label(text=f"bruh ::, ::", x=100, y=500)

conwey = np.zeros([400, 400])
active_regions = {}  # rects 40x40 (x, y)
BLK = 20

xys = []
colors = []


def update(s):
    screen.clear()
    global conwey
    t1 = time.time()
    # pg.gl.glBegin(pg.gl.GL_POINTS)
    # for y in range(len(conwey)-1):
    #     for x in range(len(conwey[0]-1)):
    #         pg.gl.glVertex2f(x, y)
    #         pg.gl.glColor3b(0, int(255 * conwey[y][x]), 0)
    # pg.gl.glEnd()
    pg.graphics.draw(160000, pg.graphics.GL_POINTS,
                     ('v2f', xys),  # [x, y]
                     ('c4B', colors))
    print(time.time() - t1)


@screen.event
def on_mouse_press(x, y, mouse, status):
    global conwey
    if mouse == 1:
        _miny, _minx = y - 5, x-5
        _maxy, _maxx = y + 5, x+5
        conwey[_miny:_maxy, _minx:_maxx] = 0.8

def lerp (a, b, w):
    return a * (1 - w) + b * w


if __name__ == "__main__":
    pg.gl.glEnable(pg.gl.GL_BLEND)
    pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)

    conwey[0] = 1
    for y in range(1, len(conwey)-2):
        conwey[y] = lerp(conwey[y-1][0], 0, 0.01)

    for y in range(len(conwey)):
        for x in range(len(conwey[0])):
            xys.extend([x, y])
            colors.extend([0, int(255 * conwey[y][0]), 0, 255])  # (0, int(255*conwey[y][0]), 0, 255)

    pg.clock.schedule_interval(update, 1 / 60.0)
    pg.app.run()