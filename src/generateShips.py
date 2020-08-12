import random
import pygame as pg
from pygame import gfxdraw as gfx
import time

from Ships import Generate


if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((500, 500))
    # random.seed(145)
    while 1:
        sim = random.choice([True, False])  # symmetrical or asymmetrical
        size = 100
        radius = size*4
        radius_diff = 5
        ang = 0.5

        blocks, cds, hull = Generate.generate_tree(20)
        screen.fill((0, 0, 0))
        hull = Generate.shrink(hull, 1)
        pg.event.pump()
        for b in blocks:
            pg.draw.rect(screen, b.color, (b.getX()-5, b.getY()-5, 10, 10))
        for line in [l for subhull in hull for l in subhull]:
            c = (255, 0,0, 150) if (255,0,0, 150)==line[0].color==line[1].color else (0,255,0, 150)
            gfx.line(screen, int(line[0].getX()), int(line[0].getY()), int(line[1].getX()), int(line[1].getY()), c)

        pg.display.flip()
        time.sleep(1)
