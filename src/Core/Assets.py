import os
import pyglet as pg

pg.resource.path = ["../assets", "../assets/ships", "../assets/"]
pg.resource.reindex()

blanc = pg.image.load('../assets/blanc.png')
# ball_img = pg.image.load(os.path.join("..", "assets", "Ball.png"))
# bolt_1 = pg.image.load(os.path.join("..", "assets", "projectiles", "bolt_1.png"))
# expl_2 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_2.png"))
# expN_1 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_1_b.png"))
# engi_1 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_1.png"))
# shld_0 = pg.image.load(os.path.join("..", "assets", "animations", "Shields", "shield_1_40x40.png"))