bound_break_vert = False
bound_break_gor = False
t = [True, True, True, True]
score = 0
FPS = 30

map_size = m_width, m_size = 3000, 3000
size = width, height = 720, 576
BLACK = 0, 0, 0
WHITE = 255, 255, 255
GREEN = 0, 255, 0
control_keys = [False,False,False,False,False]
ball_speed_limit = 10
#...

#####################      Ships       ####################

#              rotation rate    deacceleration        hull   shields type(mass)
 #                      acceleration    env. deacceleration
SHIP_CONSTANTS = [[1.6666, 0.4166, 0.0333,   0.0083,    5,      2,      1],
                  [  1.25,  0.025, 0.0125,    0.005,   15,      5,      2],
                  [   2.5, 0.0625,   0.05,   0.0125,  7.5,    2.5,      1],
                  [   1.2,   0.03,   0.01,     0.01,    2,      2,      1],
                  []]


picked_ship = 2
EXPL = 9
start_lives = 2
