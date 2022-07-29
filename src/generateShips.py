import math
import os
import random
import pygame as pg
from pygame import gfxdraw as gfx
import time

from Ships import Generate
from Ships.Generate import generate_poly

if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((500, 500))
    # random.seed(145)
    samples = (1000, 100)
    os.makedirs("imgs/train", exist_ok=True)
    os.makedirs("imgs/test", exist_ok=True)
    for folder, n_samples in zip(["imgs/train", "imgs/test"], samples):
        labels = [0] * n_samples
        for i in range(n_samples):
            temperature = max(0.0, min(1.0, random.normalvariate(0.2, 0.3)))
            sharpness = max(0.0, min(1.0, random.normalvariate(0.8, 0.3)))
            labels[i] = round((temperature + sharpness) / 2)
            img, _, _ = generate_poly(
                (500,500),
                temperature=temperature,
                sharpness=sharpness
            )
            screen.blit(img, (0,0))
            im_name = f'{folder}/{i}_tmp{temperature:.2f}-srp{sharpness:.2f}-{labels[i]}.png'
            # Generate.save_img(screen, im_name, size=(100, 100))
            pg.display.flip()
            time.sleep(1.0)
