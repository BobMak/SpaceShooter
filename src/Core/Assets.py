import os
import pygame as pg

pg.init()

blanc = pg.image.load(os.path.join("..", "assets", "blanc.png"))
green = pg.image.load(os.path.join("..", "assets", "ships", "green.png"))
bad_thing = pg.image.load(os.path.join("..", "assets", "bad_thing.png"))
guy_img = pg.image.load(os.path.join("..", "assets", "ships", "Ship1_22x24.png"))
ship_2 = pg.image.load(os.path.join("..", "assets", "ships", "Ship_2.png"))
ship_3 = pg.image.load(os.path.join("..", "assets", "ships", "wraith.png"))
turret = pg.image.load(os.path.join("..", "assets", "turret.png"))
d_mask_1 = pg.image.load(os.path.join("..", "assets", "dron_mask_1.png"))
bg_ball = pg.image.load(os.path.join("..", "assets", "ball_base_40x40.png"))
particle = pg.image.load(os.path.join("..", "assets", "particle_1.png"))

img_asteroid = pg.image.load(os.path.join("..", "assets", "asteroid.png"))
img_asteroid_1 = img_asteroid
img_asteroid_2 = pg.image.load(os.path.join("..", "assets", "asteroid_2.png"))
img_asteroid_3 = pg.image.load(os.path.join("..", "assets", "asteroid_3.png"))
img_asteroid_4 = pg.image.load(os.path.join("..", "assets", "asteroid_4.png"))
ball_img = pg.image.load(os.path.join("..", "assets", "Ball.png"))

bolt_1 = pg.image.load(os.path.join("..", "assets", "projectiles", "bolt_1.png"))
bolt_2 = pg.image.load(os.path.join("..", "assets", "projectiles", "bolt_2.png"))
bolt_3 = pg.image.load(os.path.join("..", "assets", "projectiles", "bolt_3.png"))

missile_1 = pg.image.load(os.path.join("..", "assets", "projectiles", "missile_1.png"))

expl_2 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_2.png"))
expl_3 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_3.png"))
expl_4 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_4.png"))
expl_5 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_5.png"))
expl_6 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_6.png"))
expl_7 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_7.png"))
expl_8 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_8.png"))
expl_9 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_9.png"))
expl_1 = pg.image.load(os.path.join("..", "assets", "animations", "Explosions", "Expl_1.png"))

expN_1 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_1_b.png"))
expN_2 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_2_b.png"))
expN_3 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_3_b.png"))
expN_4 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_4_b.png"))
expN_5 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_5_b.png"))
expN_6 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_6_b.png"))
expN_7 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_7_b.png"))
expN_8 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_8_b.png"))
expN_9 = pg.image.load(os.path.join("..", "assets", "animations", "Explosion_1", "ExpN_9_b.png"))

engi_1 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_1.png"))
engi_2 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_2.png"))
engi_3 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_3.png"))
engi_4 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_4.png"))
engi_5 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_5.png"))
engi_6 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_6.png"))
engi_7 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_7.png"))
engi_10 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_2.png"))
engi_11 = pg.image.load(os.path.join("..", "assets", "animations", "Engi", "engi_1.png"))

shld_0 = pg.image.load(os.path.join("..", "assets", "animations", "Shields", "shield_1_40x40.png"))
shld_1 = pg.image.load(os.path.join("..", "assets", "animations", "Shields", "shield_1_fade_40x40.png"))
shld_2 = pg.image.load(os.path.join("..", "assets", "animations", "Shields", "shield_1_fade_40x40_2.png"))
shld_3 = pg.image.load(os.path.join("..", "assets", "animations", "Shields", "shield_1_fade_40x40_3.png"))
shld_4 = pg.image.load(os.path.join("..", "assets", "animations", "Shields", "shield_1_fade_40x40_4.png"))
shld_5 = pg.image.load(os.path.join("..", "assets", "animations", "Shields", "shield_1_fade_40x40_5.png"))
shld_6 = pg.image.load(os.path.join("..", "assets", "animations", "Shields", "shield_1_fade_40x40_6.png"))
shld_7 = pg.image.load(os.path.join("..", "assets", "animations", "Shields", "shield_1_fade_40x40_7.png"))

model_BG = pg.image.load(os.path.join("..", "assets", "ModelBG.bmp"))

BG = pg.transform.scale(pg.image.load(os.path.join("..", "assets", "BG_720.png")), (1200, 1000))

menu_BG = pg.image.load(os.path.join("..", "assets", "menu_BG.png"))
menu_button = pg.image.load(os.path.join("..", "assets", "menu_button.png"))
menu_button_selected = pg.image.load(os.path.join("..", "assets", "menu_button_selected.png"))
live = pg.image.load(os.path.join("..", "assets", "1live.png"))

prj_imgs =  [bolt_1, bolt_3, bolt_2, missile_1]

expl = [expl_1, expl_2, expl_3, expl_4, expl_5, expl_6, expl_7, expl_8, expl_9]
expN = [expN_1, expN_2, expN_3, expN_4, expN_5, expN_6, expN_7, expN_8, expN_9]
engi = [engi_5, engi_3, engi_2]
shield = [shld_0, shld_1, shld_2, shld_3, shld_4, shld_5, shld_6, shld_7]
asteroid_imgs = [img_asteroid_1, img_asteroid_2, img_asteroid_3, img_asteroid_4]

SHIPS_IMGS = [guy_img, ship_2, ship_3]