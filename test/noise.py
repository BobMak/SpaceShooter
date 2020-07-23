import random
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


def update(s):
    screen.clear()
    global conwey
    for y in range(len(conwey)-1):
        # pg.graphics.draw(4, pg.graphics.GL_QUADS,
        #                  ('v2f', [0, y, 0, y + 1, 0, y, 0 + 800, y]),
        #                  ('c4B', (0, int(255*conwey[y][0]), 0, 255) * 4))
        # pg.graphics.draw(2, pg.gl.GL_POINTS,
        #                  ('v2i', (0, y, 1, y)),
        #                  ('c4B', (0, int(255 * conwey[y][0]), 0, 255) * 4))
        pg.graphics.draw(2, pg.gl.GL_POINTS,
                             ('v6i', (0, y, 1, y, 2, y, 0, y, 1, y, 2, y))
                             )
            # print(x)
        # print(y)

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

    pg.clock.schedule_interval(update, 1 / 16.0)
    pg.app.run()