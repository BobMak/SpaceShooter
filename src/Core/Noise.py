from numba import jit, cuda, prange
import pyglet as pg
import numpy as np

import matplotlib.pyplot as plt


@jit(nopython=True, parallel=False)
def smoothstep(x):
    return 3 * x ** 2 - 2 * x ** 3

@jit(nopython=True, parallel=False)
def lerp(a, b, w):
    return a * (1 - w) + b * w

@jit(nopython=True, parallel=False)
def get_noise_layer(map, rate):
    """return an array of the same size as map.
    sample one value from the map every rate steps.
    Interpolate between picked values to get the same map size"""
    noise_layer = np.zeros(map.shape, dtype=np.float32)
    ref = np.zeros(( map.shape[0] // rate +1, map.shape[1] // rate +1 ), dtype=np.float32)
    for y in prange(1, len(ref)):
        for x in prange(1, len(ref[0])):
            ref[y][x] = map[rate * y -1][rate * x -1]

    for idx_y in prange(0, len(ref)-1):
        for idx_x in prange(0, len(ref[0])-1):
            for y in prange(rate):
                w_y = smoothstep(y / rate)
                for x in prange(rate):
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

@jit(nopython=True, parallel=False)
def getNoiseEven(map, depth, persistance=0.5):
    out = np.zeros(map.shape, dtype=np.float32)
    for i in range(1, depth+1):
        out += get_noise_layer(map, int(len(map)/(2+i))) * persistance ** i
    s = out / out.max()
    return s


def getNoiseImage(size=200, rgba=[1, 1, 1, 1], depth=10, persistance=0.9):
    assert [True if 1 >= x >= 0 else False for x in rgba], "rgba values have to be within [0,1] range"
    pureNoise = np.random.rand(size, size)
    perlineNoise = getNoiseEven(pureNoise, depth, persistance)
    mapData = np.zeros((size, size, 4), dtype=np.float32)
    mapData[:, :] = np.expand_dims(perlineNoise, axis=2) * np.array(rgba) * 255
    mapData = mapData.astype(np.uint8)

    map = pg.image.ImageData(size, size, "RGBA", mapData.tobytes())
    return map


def flaten(list):
    flat = []
    for outer in list:
        for inner in outer:
            flat.append(inner)
    return flat
