import time
import pyglet as pg
import numpy as np


screen = pg.window.Window(800, 800, )
lable = pg.text.Label(text=f"bruh ::, ::", x=100, y=500)

conwey = np.zeros([400, 400])
attention_areas = {}  # rects 40x40 (x, y)
BLK = 20


def update(x):
    # Only process the active regions
    global conwey, attention_areas
    newconwey = np.copy(conwey)
    toRemove  = []
    toAdd     = []
    for a in attention_areas.values():
        active = False
        for _y in range(BLK):
            y = _y + a[1]
            for _x in range(BLK):
                x = _x + a[0]
                ssm = np.sum(conwey[y - 1:y + 2, x - 1:x + 2])
                if (ssm > 3 or ssm < 2) and conwey[y][x]:
                    newconwey[y][x] = 0
                    active = True
                    pg.graphics.draw(4, pg.graphics.GL_QUADS,
                                     ('v2f', [x * 2, y * 2, x * 2, y * 2 + 2, x * 2, y * 2, x * 2 + 2, y * 2]),
                                     ('c4B', (0,0,0,255)*4))
                elif not conwey[y][x] and ssm > 2 and ssm < 5:
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
        if np.sum(newconwey[ a[1]+BLK, a[0]:a[0]+BLK])>2:
            toAdd.append((a[0], a[1]+BLK))  # top
        if np.sum(newconwey[ a[1], a[0]:a[0]+BLK])>2:
            toAdd.append((a[0], a[1]+BLK))  # bottom
        if np.sum(newconwey[ a[1]:a[1]+BLK, a[0]])>2:
            toAdd.append((a[0], a[1]+BLK))  # left
        if np.sum(newconwey[ a[1]:a[1]+BLK, a[0]+BLK])>2:
            toAdd.append((a[0], a[1]+BLK))  # right
    for na in toRemove:
        del attention_areas[na]
    for ta in toAdd:
        attention_areas[ta]=ta
    conwey = newconwey


def update_naive():
    global conwey, attention_areas
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
    global conwey
    # print(x, y)
    if mouse == 1:
        _miny, _minx = y // 2 - 5, x//2-5
        _maxy, _maxx = y // 2 + 5, x//2+5
        conwey[_miny:_maxy, _minx:_maxx] = 1
    elif mouse == 4:  # make a glider
        _miny, _minx = y // 2 - 2, x // 2 - 2
        _maxy, _maxx = y // 2 + 2, x // 2 + 2
        conwey[_miny, _minx+1:_maxx] = 1
        conwey[_miny + 1, _maxx-1] = 1
        conwey[_miny + 2, _maxx-2] = 1
    # add initial active regions
    regy = _miny // BLK * BLK
    regx = _minx // BLK * BLK
    attention_areas[(regx, regy)]         = (regx, regy)
    attention_areas[(regx+BLK, regy)]     = (regx+BLK, regy)
    attention_areas[(regx, regy+BLK)]     = (regx, regy+BLK)
    attention_areas[(regx+BLK, regy+BLK)] = (regx+BLK, regy+BLK)
    # lable = pg.text.Label(text=f"bruh {ar1}, {ar2}", x=100, y=500)


if __name__ == "__main__":
    pg.clock.schedule_interval(update, 1 / 30.0)
    pg.app.run()