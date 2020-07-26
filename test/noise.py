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

pureNoise = np.zeros([400, 400])
active_regions = {}  # rects 40x40 (x, y)
BLK = 20
map = None

xys = []
colors = []


def update(s):
    screen.clear()
    global pureNoise, map
    pureNoise = np.random.rand(*pureNoise.shape)
    perlineNoise = getNoise(pureNoise, [200, 80, 40, 20, 5])
    mapData = []

    for y in range(len(perlineNoise)):
        for x in range(len(perlineNoise[0])):
            mapData.extend([0, int(255 * perlineNoise[y][x]), 0, 255])  # (0, int(255*pureNoise[y][0]), 0, 255)
    map = pg.image.ImageData(400, 400, "RGBA", b"".join([x.to_bytes(1, "big") for x in mapData]))
    map.blit(0, 0)
    print('ff')


@screen.event
def on_mouse_press(x, y, mouse, status):
    global pureNoise
    if mouse == 1:
        _miny, _minx = y - 5, x-5
        _maxy, _maxx = y + 5, x+5
        pureNoise[_miny:_maxy, _minx:_maxx] = 0.8


def smoothstep(x):
    """nice smooth transition instead of jig-like linear"""
    return 3*x**2 - 2 * x**3


def lerp (a, b, w):
    """Linear interpolation with a given weight"""
    return a * (1 - w) + b * w


def get_noise_layer(map, rate):
    """return an array of the same dimensions as map.
    sample one value from the map every rate steps.
    Interpolate between picked values to get the same map dimensions"""
    noise_layer = np.zeros(map.shape)
    ref = np.zeros([x // rate + 1 for x in map.shape])
    for y in range(1, len(ref)):
        for x in range(1, len(ref[0])):
            ref[y][x] = map[rate * y - 1][rate * x - 1]

    for idx_y in range(0, len(ref)-1):
        for idx_x in range(0, len(ref[0])-1):
            for y in range(rate):
                w_y = smoothstep(y / rate)
                for x in range(rate):
                    w_x = smoothstep(x / rate)
                    noise_layer[idx_y * rate + y][idx_x * rate + x] = \
                        lerp( lerp(ref[idx_y]  [idx_x], ref[idx_y]  [idx_x+1],   w_x),
                              lerp(ref[idx_y+1][idx_x], ref[idx_y+1][idx_x + 1], w_x), w_y )
    return noise_layer


def getNoise(map, li, persistance=0.5):
    out = []
    for i, l in enumerate(li):
        out.append(get_noise_layer(map, l) * persistance**i )
    return sum(out)/len(li)


def flaten(list):
    flat = []
    for outer in list:
        for inner in outer:
            flat.append(inner)
    return flat


if __name__ == "__main__":
    pg.gl.glEnable(pg.gl.GL_BLEND)
    pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)
    pg.clock.schedule_interval(update, 1)
    pg.app.run()