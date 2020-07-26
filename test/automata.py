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


def update(x):
    screen.clear()
    astr.draw()
    global pureNoise, active_regions
    newconwey = np.copy(conwey)
    toRemove  = []
    toAdd     = []
    # Only process the active regions
    for a in active_regions.values():
        active = False
        for _y in range(BLK):
            y = _y + a[1]
            for _x in range(BLK):
                x = _x + a[0]
                ssm = np.sum(conwey[y - 1:y + 2, x - 1:x + 2])
                if (ssm > 4 or ssm < 3) and conwey[y][x]:
                    newconwey[y][x] = 0
                    active = True
                    pg.graphics.draw(4, pg.graphics.GL_QUADS,
                                     ('v2f', [x * 2, y * 2, x * 2, y * 2 + 2, x * 2, y * 2, x * 2 + 2, y * 2]),
                                     ('c4B', (0,0,0,255)*4))
                elif conwey[y][x] and ssm==4:
                    active = True
                    newconwey[y][x] = 1
                    pg.graphics.draw(4, pg.graphics.GL_QUADS,
                                     ('v2f', [x * 2, y * 2, x * 2, y * 2 + 2, x * 2, y * 2, x * 2 + 2, y * 2]),
                                     ('c4B', (0, 255, 0, 200) * 4))
                elif not conwey[y][x] and ssm==3:
                    newconwey[y][x] = 1
                    active = True
                    pg.graphics.draw(4, pg.graphics.GL_QUADS,
                                     ('v2f', [x * 2, y * 2, x * 2, y * 2 + 2, x * 2, y * 2, x * 2 + 2, y * 2]),
                                     ('c4B', (0, 255, 0, 200) * 4))
        if not active:
            toRemove.append(a)
            continue
        # check bounds to see if other regions need to be checked next round.
        # Looks kinda dumb
        if np.sum(newconwey[ a[1]+BLK-1, a[0]:a[0]+BLK])>2:
            toAdd.append((a[0]// BLK * BLK, (a[1]+BLK)// BLK * BLK))  # top
        if np.sum(newconwey[ a[1], a[0]:a[0]+BLK])>2:
            toAdd.append((a[0]// BLK * BLK, (a[1]-BLK)// BLK * BLK))  # bottom
        if np.sum(newconwey[ a[1]:a[1]+BLK, a[0]])>2:
            toAdd.append(((a[0]-BLK)// BLK * BLK, a[1]// BLK * BLK))  # left
        if np.sum(newconwey[ a[1]:a[1]+BLK, a[0]+BLK-1])>2:
            toAdd.append(((a[0]+BLK)// BLK * BLK, a[1]// BLK * BLK))  # right
        # # highlight active regions
    for region in toRemove:
        del active_regions[region]
    for region in toAdd:
        active_regions[region]=region
    conwey = newconwey


def update_naive():
    global pureNoise, active_regions
    newconwey = np.copy(conwey)
    for y in range(len(conwey)//4):
        for x in range(len(conwey[0])//4):
            ssm = np.sum(conwey[y - 1:y + 2,x - 1:x + 2])
            if (ssm > 3 or ssm < 2) and conwey[y][x]:
                newconwey[y][x] = 0
            elif not conwey[y][x] and ssm == 3:
                newconwey[y][x] = 1
    conwey = newconwey


@screen.event
def on_mouse_press(x, y, mouse, status):
    global pureNoise
    if mouse == 1:
        _miny, _minx = y // 2 - 5, x//2-5
        _maxy, _maxx = y // 2 + 5, x//2+5
        conwey[_miny:_maxy, _minx:_maxx] = 1
    elif mouse == 4:  # make a glider
        _miny, _minx = y // 2 - 2, x // 2 - 2
        _maxy, _maxx = y // 2 + 2, x // 2 + 2
        glider = [
            [1, 0, 0, ],
            [1, 0, 1, ],
            [1, 1, 0, ],
        ]
        # glider = glider[::]
        for _y in range(3):
            for _x in range(3):
                conwey[_miny + _y][_minx + _x] = glider[_y][_x]
    # add initial active regions
    regy = _miny // BLK * BLK
    regx = _minx // BLK * BLK
    active_regions[(regx, regy)]             = (regx, regy)
    active_regions[(regx + BLK, regy)]       = (regx + BLK, regy)
    active_regions[(regx, regy + BLK)]       = (regx, regy + BLK)
    active_regions[(regx + BLK, regy + BLK)] = (regx + BLK, regy + BLK)
    # lable = pg.text.Label(text=f"bruh {ar1}, {ar2}", x=100, y=500)


if __name__ == "__main__":
    pg.gl.glEnable(pg.gl.GL_BLEND)
    pg.gl.glBlendFunc(pg.gl.GL_SRC_ALPHA, pg.gl.GL_ONE_MINUS_SRC_ALPHA)

    pg.clock.schedule_interval(update, 1 / 16.0)
    pg.app.run()