import numpy as np
import random, pygame, copy
from ShipParams import *
import Assets
import Classes
import Controls

def get_dist(dx, dy):
    return np.sqrt(dx**2 + dy**2)

def angle_diff(a1, a2):
    """angle_1 - angle_2 with regards to used angle system"""
    a = a1 - a2
    if abs(a) > 180:
        return np.sign(a)*360 - a
    else:
        return a

def shields(source):

    if len(source.shields) == 0:
        shld_obj = Classes.Shield(Assets.shield, source.rect.width+10,
                                  source.rect.height+10, source.rect.left,
                                  source.rect.top, source, 1)

        shld_obj.rotate(source.look_dir)
        source.sh_add(shld_obj)
        Assets.effects.add(shld_obj)

def shot(shoter, direction, bolt):

    skipped_len = shoter.rect.height//2
    shot = 0
    shot = Classes.Projectile(bolt, shoter.rect.centerx,
                              shoter.rect.centery, Assets.prj_distances[bolt])
    shot.look_dir = shoter.look_dir
    shot.rect.centerx = (shoter.rect.centerx
                        - skipped_len*np.cos(np.deg2rad(shot.look_dir
                                                              + 90)))
    shot.rect.centery = (shoter.rect.centery
                        - skipped_len*np.sin(np.deg2rad(shot.look_dir
                                                              + 90)))

    shot.speed = [Assets.prj_speeds[bolt]
                   *np.cos(np.deg2rad(shoter.look_dir-90)),
                  Assets.prj_speeds[bolt]
                   *np.sin(np.deg2rad(shoter.look_dir-90))]

    shot.rotate(0)
#       Operates with last 'keys' list
#       Closure functions

def ship_assign(picked_ship, lives, player):
    '''Assign all properties to given ship. Usually when creating new instance
    of ship'''
    ship = Classes.Player(Assets.SHIPS_IMGS[picked_ship],
                     width//2, height//2,
                     complex_sh=picked_ship-1, bolt=picked_ship,
                     lives=lives, width=None, height=None, player=player)
    ship.rotate(0)
    ship.arr_input = Controls.ABILITIES[picked_ship]

    ship.ROTATION = SHIP_CONSTANTS[picked_ship][0]
    ship.ACCELERATION = SHIP_CONSTANTS[picked_ship][1]
    ship.DEACCELERATION = SHIP_CONSTANTS[picked_ship][2]
    ship.ENV_DEACCELERATION = SHIP_CONSTANTS[picked_ship][3]
    ship.HP = SHIP_CONSTANTS[picked_ship][4]
    ship.S_HP = SHIP_CONSTANTS[picked_ship][5]
    ship.type = SHIP_CONSTANTS[picked_ship][6]

    return ship

def draw_rotating(obj):

    rect = obj.rotated_image.get_rect()
    rect.center = (obj.rect.center)
    Assets.screen.blit(obj.rotated_image, rect)

def blur(obj, speed):
    '''blur effect along the speed direction'''
    rect = obj.rotated_image.get_rect()
    img = obj.rotated_image_alpha

    for x in range(int(speed)//3):
        rect.centerx = obj.rect.centerx + obj.speed[0]//(x+3)
        rect.centery = obj.rect.centery + obj.speed[1]//(x+3)
        Assets.screen.blit(img, rect)
        rect.centerx = obj.rect.centerx - obj.speed[0]//(x+3)
        rect.centery = obj.rect.centery - obj.speed[1]//(x+3)
        Assets.screen.blit(img, rect)

def orbit_rotate(center, obj, d_ang, dist = 0, ang = -20):
    """orbit_rotate(center, obj, d_ang, dist = 0, ang = -20)
    rotate 'obj' by the orbit of 'center' on range of 'dist'
    from center of 'center' by angle 'ang'. 'obj' has to have angle argument"""
    if ang == -20:

        dx = obj.rect.centerx - center.rect.centerx
        dy = obj.rect.centery - center.rect.centery

        if dx > 0 and dy < 0:
            ang = abs(np.rad2deg(np.arctan(dx/dy)))
        elif dx < 0 and dy < 0:
            ang = abs(np.rad2deg(np.arctan(dy/dx)))
        elif dx > 0 and dy > 0:
            ang = abs(np.rad2deg(np.arctan(dy/dx)))
        elif dx < 0 and dy > 0:
            ang = abs(np.rad2deg(np.arctan(dx/dy)))
        else:
            ang = 90
    else:

        obj.orbit_ang += d_ang

        if obj.orbit_ang > 360:
            obj.orbit_ang += -360
        elif obj.orbit_ang < 0:
            obj.orbit_ang += 360

        ang = obj.orbit_ang

    if dist == 0:
        # dist = np.sqrt((obj.rect.centerx - center.rect.centerx)**2 +
        # (obj.rect.centery - center.rect.centery)**2)
        pass

    obj.rect.centerx = center.rect.centerx + dist*(np.sin(np.deg2rad(ang)))
    obj.rect.centery = center.rect.centery + dist*(np.cos(np.deg2rad(ang)))

def orbit_eliptic(center, obj):
    """
    orbit_eliptic(center, obj)
    obj orbits center on median distance of 'm_dist' with angular speed d_ang.
    'orbit_coef' shows how many times in one full turn 'obj' reaches
    its perigee or apsis.
    'd_dist' is the differance between apsis/perigee and the median
    """

    obj.distance += obj.d_dist*obj.d_dist_dir

    if obj.distance < obj.min_dist:
        obj.d_dist_dir = 1

    elif obj.distance > obj.max_dist:
        obj.d_dist_dir = -1

    orbit_rotate(center, obj, obj.d_ang, obj.distance, obj.orbit_ang)

def draw_triangle(player, color, dist_to_edg, width):
    bufx1 = 0
    bufx2 = 0
    bufx3 = 0
    bufy1 = 0
    bufy2 = 0
    bufy3 = 0
    bufx1 = (player.rect.centerx
          + dist_to_edg * np.cos(np.deg2rad(player.look_dir - 90)))
    bufx2 = (player.rect.centerx
          + dist_to_edg * np.cos(np.deg2rad(player.look_dir + 120 - 90)))
    bufx3 = (player.rect.centerx
          + dist_to_edg * np.cos(np.deg2rad(player.look_dir - 120 - 90)))
    bufy1 = (player.rect.centery
          + dist_to_edg * np.sin(np.deg2rad(player.look_dir - 90)))
    bufy2 = (player.rect.centery
          + dist_to_edg * np.sin(np.deg2rad(player.look_dir + 120 - 90)))
    bufy3 = (player.rect.centery
          + dist_to_edg * np.sin(np.deg2rad(player.look_dir - 120 - 90)))
    pygame.draw.polygon(Assets.screen, color,
                        ((bufx1, bufy1), (bufx2, bufy2), (bufx3, bufy3)), width)

def bound_collision(obj):
    global bound_break_vert
    global bound_break_gor
    global control_keys

    if obj.rect.left < 0 or obj.rect.right > width:

        #control_keys[0:4] = False, False, False, False
        #if bound_break_gor == False:
        obj.speed[0] = -obj.speed[0]
        #   bound_break_gor = True
    else:
        bound_break_gor = False
    if obj.rect.top < 0 or obj.rect.bottom > height:
       # control_keys[0:4] = False, False, False, False
        #if bound_break_vert == False:
        obj.speed[1] = -obj.speed[1]
        #bound_break_vert = True
    else:
        bound_break_vert = False
    return bound_break_gor, bound_break_vert

def bound_pass(obj):

    if (obj.position[0] < -obj.rect.width
     or obj.position[0] > width):

        # obj.rect = obj.rect.move((-(width + obj.rect.width) * np.sign(obj.rect.centerx)), 0)
        # obj.rect.centerx += -(width + obj.rect.width) * np.sign(obj.rect.centerx)
        obj.position[0] += -(width + obj.rect.width) * np.sign(obj.rect.x)
        # except: pass

    if (obj.position[1] < -obj.rect.height
     or obj.position[1] > height):
        # obj.rect = obj.rect.move(0, (-(height + obj.rect.width) * np.sign(obj.rect.centery)))
        obj.position[1] += -(height + obj.rect.height) * np.sign(obj.rect.y)
        # except: pass

def move_movable():
    for object in Assets.movable:
        # modify position to avoid loss of <1 values when moving
        object.modify_position()

def spawn_wave(realGuy):
    level = Assets.level
    for i in range(Assets.levels[level][0]):
        if random.choice([True, False]):
            proX = random.choice([random.randint(-20,0),
                                  random.randint(width, width+20)])
            proY = random.randint(-20, height+20)
        else:
            proX = random.randint(-20, width+20)
            proY = random.choice([random.randint(-20,0),
                                  random.randint(height, height+20)])

        x = Classes.Adv_Asteroid(Assets.levels[level][1]+1, proX, proY, 4, [0,0])

    Assets.level += 1

def FX_explosion(x, y, xpl=Assets.expl, radius=(30,30)):

    obj = Classes.Animation(xpl, radius[0], radius[1], x, y, True)
    obj.rect.centerx += - 20
    obj.rect.centery += - 20

    Assets.effects.add(obj)

def FX_engine_mark(source):
    object = 0
    object = Classes.Animation(Assets.engi, 10, 10,
                               source.rect.centerx, source.rect.centery)
    object.look_dir = source.look_dir
    object.rotate(0)
    object.speed = source.speed

    object.rect.centerx = (source.rect.centerx
                        + source.rect.height//2
                          * np.cos(np.deg2rad(object.look_dir+90)))
    object.rect.centery = (source.rect.centery
                        + source.rect.height//2
                          * np.sin(np.deg2rad(object.look_dir+90)))

    speed0 = np.cos(np.deg2rad(copy.deepcopy(object.look_dir+90)))*3
    speed1 = np.sin(np.deg2rad(copy.deepcopy(object.look_dir+90)))*3

    Assets.effects.add(object)
