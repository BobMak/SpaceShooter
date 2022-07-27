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
        symmetric = False # random.choice([True, False])  # symmetrical or asymmetrical
        size = 100
        radius = size*4
        radius_diff = 5
        ang = 0.5

        # blocks, cds, hull = Generate.generate_tree(30, symmetry=False)
        blocks, hull = Generate.generate_normals(
            center=(0, 0),  # (screen.get_width()//2, screen.get_height()//2)
            npoints=5,
            nrecurs=2,
            std=25.0,
            dstd=7.0,
            leafhull=True
        )
        screen.fill((0, 0, 0))
        hull = Generate.shrink(hull, 5, symmetry=symmetric)
        pg.event.pump()
        # for b in blocks:
        #     # pg.draw.rect(screen, b.color, (b.getX()-5, b.getY()-5, 10, 10))
        #     pg.draw.circle(screen, b.color, (b.getX(), b.getY()), 2)
        # for line in [l for subhull in hull for l in subhull]:
        #     c = (255, 0,0, 150) if (255,0,0, 150)==line[0].color==line[1].color else (0,255,0, 150)
        #     gfx.line(screen, int(line[0].getX()), int(line[0].getY()), int(line[1].getX()), int(line[1].getY()), c)
        # fill polygon for the outermost hull
        for subhull in hull:
            gfx.filled_polygon(screen, [(p.getX(), p.getY()) for l in subhull for p in l], (0, 255, 0, 100))

        pg.display.flip()
        time.sleep(1)
