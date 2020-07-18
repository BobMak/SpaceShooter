import random
import pygame as pg
import time

from Map import Maps

# Do a graph like map
# Every point is a system

if __name__ == "__main__":
    verse = Maps.Verse()
    pg.init()
    screen = pg.display.set_mode((500, 500))
    random.seed(145)
    while 1:
        sim = random.choice([True, False])  # symmetrical or asymmetrical
        screen.fill((0, 0, 0))
        pg.display.flip()
        time.sleep(2)

