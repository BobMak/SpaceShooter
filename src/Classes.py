import pickle
import random, copy
import numpy as np
import pygame.gfxdraw as gfx
from src import Funcs, Scripts, State
from src.Assets import *


class Vulnerable:
    """
    Inherited by all objects that can be damaged.
    """
    def __init__(self, hp):
        self.hp = hp

    def damage(self, damage):
        self.hp += -max(0, damage)


class Moving:
    """
    Inherited by all classes that can move by themselves.
    """
    def __init__(self):
         self.speed = [0.0, 0.0]

         self.position = [self.rect.x, self.rect.y]

         State.movable.add(self)

    def modify_position(self):
        "modifyes position with respect to <1 values of acceleration"
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]

        self.rect = pygame.Rect(self.position[0], self.position[1],
                                self.rect.width, self.rect.height)

    def slow_down(self):
        pass
        # self.speed[0] += (self.ENV_DEACCELERATION
        #                   *abs(np.cos(np.deg2rad(self.look_dir-90.0)))
        #                   *-np.sign(self.speed[0]))
        #
        # self.speed[1] += (self.ENV_DEACCELERATION
        #                   *abs(np.sin(np.deg2rad(self.look_dir-90.0)))
        #                   *-np.sign(self.speed[1]))

    def accelerate(self, temp):

        self.speed[0] += temp*np.cos(np.deg2rad(self.look_dir-90.0))
        self.speed[1] += temp*np.sin(np.deg2rad(self.look_dir-90.0))


class Colliding(pygame.sprite.Sprite, Moving):

    def __init__(self, rects: [(int, float, float)], source, groups):
        """
        Collision rect container for more complex forms.
        should be rotated around source object with "orbit_rotate".
        Composed of one or more squares that should represent an approximate shape of the source
        :param rects: [(side length,
                        distance from source center,
                        angle between line connecting centers and vertical axis),
                        ...]
        :param source: source object
        :param groups: all groups collision detection should work with
        """

        pygame.sprite.Sprite.__init__(self)
        self.rects = []
        for rec in rects:
            self.rects.append((pygame.Rect((source.rect.x + (np.deg2rad(np.cos(rec[2])) * rec[1])),
                                          (source.rect.y + np.deg2rad(np.sin(rec[2])) * rec[1]),
                                          rec[0], rec[0]), rec[1], rec[2]))

        self.speed = source.speed
        self.source = source

        Moving.__init__(self)

    def check_against_group(self, group, ignore_group):
        for rec in self.rects:
            for i in pygame.sprite.spritecollide(rec, group, 0):
                if i not in ignore_group:
                    self.collide(i)
                    i.collide(self)
                    # Check against one collision at a time
                    return

    def collide(self, *args):
        """What happens when that collides?"""
        raise NotImplementedError('Collide behaviour not assigned!')


class Object(pygame.sprite.Sprite):

    def __init__(self, image, x, y, width=None, height=None):
        """
        Sprite with an assigned image spawned at point x y.
        :param image,
        :param x,
        :param y,
        :param width=None (Defaults to that of image)
        :param height=None (Defaults to that of image)
        """
        self.look_dir = 0
        self.rotated_image = 0
        self.rotated_rect = 0
        self.radius = None
        self.dmg = None
        self.time_count = 0
        self.timer = 0
        self.type = 0
        self.updates = []

        pygame.sprite.Sprite.__init__(self)

        if width:
            self.image = pygame.transform.scale(image, (width, height))
            self.image_alpha = pygame.transform.scale(copy.copy(image),
                                                      (width, height))
            alpha = 128
            self.image_alpha.fill((255, 255, 255, alpha),
                                  None, pygame.BLEND_RGBA_MULT)

        else:
            self.image = image
            self.image_alpha = copy.copy(image)
            alpha = 128
            self.image_alpha.fill((255, 255, 255, alpha),
                                  None, pygame.BLEND_RGBA_MULT)

        self.rotated_image = image
        self.rotated_image_alpha = image

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rotated_rect = self.rect

        self.rect.centerx = x
        self.rect.centery = y
        self.radius = self.rect.width

        # movable.add(self)

    def rotate(self, dir):

        # Ensure that look_dir is in range [0 - 360)
        if self.look_dir > 359:
            self.look_dir += dir - 360
        elif self.look_dir < 0:
            self.look_dir += 360 + dir
        else:
            self.look_dir += dir

        self.rotated_image = pygame.transform.rotate(self.image,
                                                     -self.look_dir)
        self.rotated_image_alpha = pygame.transform.rotate(self.image_alpha,
                                                           -self.look_dir)

    def get_aim_dir(self, aim):
        """
        Returns the angle specifying direction to 'aim' object
        """
        x = None
        dx = self.rect.centerx - aim.rect.centerx
        dy = self.rect.centery - aim.rect.centery

        if dx > 0 and dy < 0:
            aim_dir = abs(np.rad2deg(np.arctan(dx/dy)))
        elif dx < 0 and dy < 0:
            aim_dir = abs(np.rad2deg(np.arctan(dy/dx)))
        elif dx > 0 and dy > 0:
            aim_dir = abs(np.rad2deg(np.arctan(dy/dx)))
        elif dx < 0 and dy > 0:
            aim_dir = abs(np.rad2deg(np.arctan(dx/dy)))
        else:
            aim_dir = 0

        if dx < 0 and dy > 0:
            pass

        elif dx < 0 and dy < 0:
            aim_dir += 90

        elif dx > 0 and dy < 0:
            aim_dir += 180

        elif dx > 0 and dy > 0:
            aim_dir += 270

        return aim_dir

    def get_distance(self, obj):
        """returns distance to object x"""

        return np.sqrt((self.rect.x - obj.rect.x)**2
                       + (self.rect.y - obj.rect.y)**2)

    def get_real_distance(self, obj):
        """get_real_distance(obj)
        the shortest distance to object 'obj' with regards
        to linked bounds of the map, comparing distance
        on screen to distances to 8 projections of aim on sides
        and corners of map"""
        all_directions_distances = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                a = (self.rect.centerx
                     - (obj.rect.centerx + x * (State.WIDTH + obj.rect.width)))
                b = (self.rect.centery
                     - (obj.rect.centery + y * (State.HEIGHT + obj.rect.height)))
                dist = np.sqrt(a**2 + b**2)
                all_directions_distances.append(dist)

        return min(all_directions_distances)

    def get_closest_aim_dir(self, aim):
        """
        returns the angle of closest position of aim with respect to looped nature of the map.
        """
        all_directions_distances = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                a = (self.rect.centerx
                     - (aim.rect.centerx + x * (State.WIDTH + aim.rect.width)))
                b = (self.rect.centery
                     - (aim.rect.centery + y * (State.HEIGHT + aim.rect.height)))

                dist = np.sqrt(a**2 + b**2)
                all_directions_distances.append(dist)

        best = all_directions_distances.index(min(all_directions_distances))

        if best < 3: x = -1
        elif best > 5: x = 1
        else: x = 0
        if (best+1)%3 == 0: y = 1
        elif best in [1, 3, 6]: y = 0
        else: y = -1
        a = aim.rect.centerx + x*(State.WIDTH + aim.rect.width)
        b = aim.rect.centery + y*(State.HEIGHT + aim.rect.height)
        aim = Object(blanc, a, b)
        return self.get_aim_dir(aim)

    def update(self):
        """Execute all pending callbacks for the object every logic tick!"""
        for f in self.updates:
            f()


class FX(pygame.sprite.Sprite, Moving):

    def __init__(self, rect, duration, fading=None, color=None, enlarging=None, speed=None):
        """

        :param rect: location
        :param duration:
            effect life duration in ticks
        :param fading:
            ((int [1,255)) num points to fade per one update (not per sec) out of 255,
             (int) num of LOGIC ticks before update)
        :param color:
            (r, g, b, a)
        :param enlarging:
            ((int) pixels to enlarge per tick, num of ticks before enlarge update)
        :param speed:
        """

        pygame.sprite.Sprite.__init__(self)

        self.timer = duration
        self.time_count = 0
        self.rect = rect

        # Requires rect to already be there
        Moving.__init__(self)

        State.time_dependent.add(self)
        self.updates = []

        if fading:
            self.fading_count = 0
            self.fading_sum = 0
            self.fading = fading[0]
            self.fading_tempo = fading[1]
            self.updates.append(self.fade)

        if color:
            self.color = color
        else:
            self.color = (255, 255, 255, 255)

        if enlarging:
            self.enlarging_count = 0
            self.enlarging_summ = 1
            self.enlarging = enlarging[0]
            self.enlarging_tempo = enlarging[1]
            self.updates.append(self.enlarge)

        if speed:
            self.speed = speed

    def fade(self):

        self.fading_count += 1

        if self.fading_count > self.fading_tempo:
            self.fading_count = 0

            self.fading_sum += self.fading
            self.color = (self.color[0], self.color[1], self.color[2], self.color[3] - self.fading_sum)

            if self.fading_sum > 230:
                self.kill()
                return

    def enlarge(self):

        self.enlarging_count += 1
        if self.enlarging_count > self.enlarging_tempo:
            self.enlarging_count = 0
            self.enlarging_summ += self.enlarging
            if self.enlarging_summ > 250:
                self.kill()
                return
            self.rect.width += self.enlarging
            self.rect.height += self.enlarging

    def update(self, *args):
        for f in self.updates:
            f(*args)


class FX_Glow(FX):
    """
    FX_Glow(rect, duration, radius, length, color, speed=(0,0))
    """
    def __init__(self, rect, duration, radius, length, color, speed=(0,0), fading=None):

        FX.__init__(self, rect, duration, color=color, speed=speed, fading=fading)
        self.radius = radius
        self.color = color
        self.length = length
        self.speed = speed
        State.glow.add(self)
        self.updates.append(self._draw)

    #draw
    def _draw(self):
        """
        drawing funcition
        """
        for x in range(self.length):
            pygame.gfxdraw.filled_circle(State.screen, self.rect.centerx,
                                         self.rect.centery, self.radius + x,
                                         self.color)


class FX_Track(FX):
    '''
    FX_Track(image, rect, duration, fading=None,
             enlarging=None, rotating=None)
    :duration - in logic ticks (there is LOGIC_PER_SECOND ticks per second).
    :fading - [x, y], where x is the rate from 0 (no fade)
    to 255 (max fade) with which effect will fade each y frames.
    :enlarging - [x, y], x - rate of effect's size deviation
    per y frames. 0-1 will shrink the effect, while >1 - enlarge.
    :rotating - [x, y], x - the angle (degrees) on which
    the effect is rotated per y frames.
    :color - set the color for effect image.
    :look_dir - initial angle (degrees)
    :speed - speed (vector [dx, dy])

    Tracks take significantly more computations if y is lower
    and duration time is higher.
    '''

    def __init__(self, image, rect, duration,
                fading=None, enlarging=None, rotating=None, color=None,
                look_dir=None, speed=None):
        '''density - [0-1]'''
        FX.__init__(self, rect, duration, fading=fading, color=color, enlarging=enlarging, speed=speed)

        self.updates.append(self._update)

        self.look_dir = 0

        self.image = pygame.transform.scale(image, (rect.width, rect.height))

        if look_dir:
            self.look_dir = look_dir
            self.rotated_image = pygame.transform.rotate(self.image,
                                                        -self.look_dir)
            self.image = pygame.transform.rotate(self.image,
                                                -self.look_dir)
            self.rotated_image_base = pygame.transform.rotate(self.image,
                                                             -self.look_dir)
        else:
            self.rotated_image = copy.copy(self.image)
            self.rotated_image_base = copy.copy(self.image)

        if rotating:
            self.rotating = rotating[0]
            self.rotating_tempo = rotating[1]
            self.updates.append(self.rotate)

        State.effects.add(self)

    def rotate(self):
        self.rotating_count += 1

        if self.rotating_count > self.rotating_tempo:
            self.rotating_count = 0

            self.look_dir += self.rotating
            self.rotated_image = pygame.transform.rotate(self.image, -self.look_dir)

    def _update(self):
        self.rotated_image_base.fill(self.color,
                                     None, pygame.BLEND_RGBA_MULT)
        self.rotated_image = copy.copy(self.rotated_image_base)
        if self.enlarging:
            self.rotated_image = pygame.transform.scale(self.rotated_image,
                                                        (self.rect.width,
                                                         self.rect.height))


class FXLaser(FX_Glow):

    def __init__(self, rect1, rect2, duration, radius, length, color, speed):
        FX_Glow.__init__(self, rect=rect1, duration=duration, radius=radius, length=length, color=color, speed=speed,
                         fading=())
        FX_Glow(rect=rect2, duration=duration, radius=radius, length=length, color=color, speed=speed)
        self.rect1 = rect1
        self.rect2 = rect2
        self.updates.append(self._draw)

        tan_ang = (rect1.y - rect2.y) / (rect1.x - rect2.x)
        self.perp_dx = np.sin(tan_ang)
        self.perp_dy = np.sin(tan_ang)

    def _draw(self):
        gfx.line(State.screen, self.rect1.x, self.rect1.y, self.rect2.x, self.rect1.y, color=self.color)
        for n in range(self.radius):
            gfx.line(State.screen,
                     self.rect1.x + self.perp_dx, self.rect1.y + self.perp_dy,
                     self.rect2.x + self.perp_dx, self.rect1.y + self.perp_dy, color=self.color)
            gfx.line(State.screen,
                     self.rect1.x - self.perp_dx, self.rect1.y - self.perp_dy,
                     self.rect2.x - self.perp_dx, self.rect1.y - self.perp_dy, color=self.color)


class Player(Object, Moving, Vulnerable):

    def __init__(self, image, x, y, lives, bolt=0,
                 complex_sh=-1, player=True, width=None, height=None):
        '''
        :param image
        :param x
        :param y
        :param lives
        :param bolt=0
        :param complex_sh=-1
        :param width=None,
        :param height=None)
        '''
        self.bolt = 0
        self.arr_input = []
        self.player_hull_group = pygame.sprite.Group()
        self.turrets = pygame.sprite.Group()
        self.orbiting = pygame.sprite.Group()
        self.mounts = []

        self.hull_group_ang = 0

        self.HP = 10
        self.MAX_HP = 10
        self.S_HP = 10
        self.MAX_S_HP = 10
        self.ROTATION = 10
        self.ACCELERATION = 1
        self.DEACCELERATION = 0.5
        self.ENV_DEACCELERATION = 0.25

        space_lock = False
        special_lock = False
        missile_lock = False
        self.locks = [space_lock, special_lock, missile_lock]

        self.speed = [0,0]
        self.lives = lives
        super().__init__(image, x, y, width=width, height=height)
        Moving.__init__(self)
        Vulnerable.__init__(self, State.SHIP_HP[complex_sh])
        """#################FIX HP###################"""

        if player == True:

            self.add(State.player_group)

            for i in range(lives):
                r = Object(live,270 + 35*(1+i),20,30, 30)
                r.add(State.interface)
                State.movable.remove(r)

            for x in State.complex_rects[complex_sh]:
                b = Colliding(x[0], x[1], x[2], x[3], self)
                self.player_hull_group.add(b)

        self.bolt = bolt

        self.time_count_fire = 0
        self.timer_fire = State.prj_cooldown[bolt]

        self.time_count_special = 0
        self.timer_special = State.spec_cooldown[complex_sh]

        self.time_count_missile = 0
        self.timer_missile = State.prj_cooldown[State.n_bolts + bolt]

        self.counts = [self.time_count_fire, self.time_count_special,
                       self.time_count_missile]

        self.timers = [self.timer_fire, self.timer_special,
                       self.timer_missile]

        self.distance = 0
        self.orbit_ang = 0
        self.player = player

        self.updates.append(self._player_update)

    def destroy(self):

        self.kill()
        self.rotate(0)
        self.speed = [0,0]
        Funcs.FX_explosion(self.rect.centerx, self.rect.centery)

        if self.player == True:

            for x in self.mounts:
                x.kill()
            for x in self.player_hull_group:
                x.kill()
            self.lives += -1

            if self.lives > -1:
                pygame.time.set_timer(pygame.USEREVENT+2, 500)
            else:
                # graphics thread termination call
                pygame.time.set_timer(pygame.USEREVENT+5, 10)
                with open('save.pkl', 'wb') as f:
                    pickle.dump(State.save, f, pickle.HIGHEST_PROTOCOL)

                Scripts.death_menu()

    def damage(self, dmg):

        self.HP += -max(0, dmg)
        if self.HP < 0:
            self.destroy()
            if self.player == True:
                return True

    def show_HP(self):
        gfx.box(State.screen, (10, 10, self.HP * 100 / self.MAX_HP, 20), (0, 255, 0, 50))

    def m_add(self, mounted):
        self.mounts.append(mounted)

    def scan(self):
        min_dist = State.asteroids.sprites[0]

        for i in State.asteroids:
            dist = np.sqrt((self.rect.x - i.rect.x)**2
                         + (self.rect.y - i.rect.y)**2)
            if dist < min_dist:
                min_dist = dist

        return min_dist

    def fire(self):

        if self.locks[0] == False:
            self.locks[0] = True
            Funcs.shot(self, self.look_dir, self.bolt)

    def _player_update(self):
        for n in range(len(self.locks)):
            if self.locks[n]:
                self.counts[n] += 1
                if self.timers[n] < self.counts[n]:
                    self.counts[n] = 0
                    self.locks[n] = False

        # TODO: Add to generic toExecute list
        for x in self.turrets:
            x.auto_fire()

        for x in self.orbiting:
            x.active()


class Mounted(Object):
    '''
    Mounted(image, mounted_on, distance = 20, look_dir = 0,
               width = 20, height = 20, restriction = None)
    '''

    mounted_on = None
    aim = None
    aim_dir = None
    orbit_ang = None

    # elliptic orbiting parameters
    d_ang = 1   # unmounted orbiting speed
    min_dist = 10
    max_dist = 5
    orbit_coef = 120  # Degrees before changing direction of distance movement

    distance = 0
    d_dist = 0
    d_dist_dir = -1     # 1 or -1 -- is object getting closer or further

    def __init__(self, image, mounted_on,
                 distance = 20, look_dir = 0,
                 width = 20, height = 20,
                 restriction = None):

        super().__init__(image, width, height,
                         (mounted_on.rect.x + mounted_on.rect.width//4
                          + distance*np.cos(np.deg2rad(mounted_on.look_dir
                                                            + look_dir -90))),
                         (mounted_on.rect.y + mounted_on.rect.height//4
                          + distance*np.sin(np.deg2rad(mounted_on.look_dir
                                                            + look_dir -90)))
                        )

        self.look_dir = mounted_on.look_dir + look_dir
        self.restriction = restriction
        self.mounted_on = mounted_on
        self.distance  = distance
        self.speed = mounted_on.speed
        if look_dir == 0:
            self.orbit_ang = mounted_on.look_dir-180
        else:
            self.orbit_ang = mounted_on.look_dir+look_dir

    def aim(self, aim):
        x = (self.look_dir - self.get_aim_dir(aim))
        if x < 5 and x > -5:
            return True
        elif abs(x) > 180:
             self.rotate(5*np.sign(x))
        else:
             self.rotate(-5*np.sign(x))

    def init_orbit(self, orbit_coef, d_ang, min, max, distance):
        self.min_dist = min
        self.max_dist = max
        self.d_ang = d_ang
        self.distance = distance
        self.orbit_coef = orbit_coef
        self.d_dist = 30*d_ang/orbit_coef
        self.mounted_on.orbiting.add(self)


class Turret(Mounted):
    """Turret(image, radius, mounted_on, groups = None,
              distance = 20, look_dir = 0,
              width = 20, height = 20,
              restriction = None, bg = bg_ball)
    """

    def __init__(self, image, radius, mounted_on,
                groups = None, distance = 20, look_dir = 0,
                width = 20, height = 20, restriction = None, bg = bg_ball):

        super().__init__(image, mounted_on, distance, look_dir,
                        width, height, restriction)
        self.interesting = [State.asteroids]
        self.in_range = []

        self.radius = radius
        self.locked = None
        self.bg = pygame.transform.scale(bg, (width-6, height-6))
        self.bg_rect = bg.get_rect()

        if groups != None:
            for i in groups:
                self.interesting.append(i)

    def set_aim(self, group):
        b = self.interesting.pop(self.interesting.index('group'))
        self.interesting.insert(0, b)

    def scan(self, group):

        a = Object(blanc, self.radius, self.radius,
                    self.rect.centerx, self.rect.centery)

        pygame.gfxdraw.circle(State.screen, self.rect.centerx, self.rect.centery,
                              self.radius, (0,255,0,50))

        for x in group:
            if pygame.sprite.collide_circle(a, x):
                if x not in self.in_range:
                    self.in_range.append(x)
        a.kill()


class TPreAim(Turret):

    mode = 2

    def __init__(self, image, radius, mounted_on, bolt_number, cooldown,
                groups = None, distance = 20, look_dir = 0,
                width = 20, height = 20, restriction = None):
        """
        Turret shoting prjoectiles with predictions of aim's
        position by its speed.
        'prj_speed' defines speed of projectiles.
        'cooldown' - in seconds.
        'bolt_numer' - index of given bolt in bolts' lists
        """

        super().__init__(image, radius, mounted_on, groups, distance,
                         look_dir, width, height, restriction)

        self.bolt_number = bolt_number
        self.bolt_img = prj_imgs[bolt_number]
        self.prj_speed = State.prj_speeds[bolt_number]

        self.predict_pos = Object(ball_img, 1, 1, -50, 1)
        self.blocked = False
        self.timer = cooldown * State.FPS
        self.time_count = 0
        self.add(mounted_on.turrets)

        mounted_on.m_add(self)




class ScriptMob(Player):

    close_range = 20
    goal = None
    to_do_list = []

    def __init__(self, image, x, y, picked_ship=0):

        super().__init__(image, x, y, lives=1, player=False)
        self.ROTATION = State.SHIP_CONSTANTS[picked_ship][0]
        self.ACCELERATION = State.SHIP_CONSTANTS[picked_ship][1]
        self.DEACCELERATION = State.SHIP_CONSTANTS[picked_ship][2]
        self.ENV_DEACCELERATION = State.SHIP_CONSTANTS[picked_ship][3]
        self.HP = State.SHIP_CONSTANTS[picked_ship][4]
        self.S_HP = State.SHIP_CONSTANTS[picked_ship][5]

    def assign_goal(self, obj=None, x=None, y=None):
        """
        assign_goal(obj=None, x=None, y=None)
        interface function.
        Assign a goal by passing the object obj (must have rect attribute)
        or giving the coordinats of the goal.
        """

        if obj == None:
            if x == None:
                print('No goal given. Both obj and x are None')
            self.goal = Object(blanc, x, y)
        else:
            self.goal = obj

    def go(self):
        """
        go()
        Perform actions to approach the goal
        """
        dist = self.get_distance(self.goal)

        if dist > self.close_range:
            speed_mod = np.sqrt(self.speed[0]**2+self.speed[1]**2)
            # If speed is small, turn in the direction of goal,
            # otherwise, in the direction allowing greater speed vecror change
            if speed_mod < 1:
                t = self.look_dir - abs(self.get_aim_dir(self.goal))
            else:
                ang = np.arctan(self.speed[0]/self.speed[1])
                spe = Object(blanc,
                            int(self.rect.centerx+30*np.sin(ang)
                                *np.sign(self.speed[1])),
                            int(self.rect.centery+30*np.cos(ang)
                                *np.sign(self.speed[1])))

                true_ang = self.get_aim_dir(self.goal) - self.get_aim_dir(spe)
                spe.kill()
                if true_ang < -180 or true_ang > 180:
                    true_ang = -360*np.sign(true_ang) + true_ang

                if true_ang < -90 or true_ang > 90:
                    t = self.get_aim_dir(self.goal)
                else:
                    t = self.get_aim_dir(self.goal) + true_ang

                # true_ang = self.get_aim_dir(self.goal) - true_ang
                t = self.look_dir - t
                if t > 360 or t < -360:
                    t += -360*np.sign(t)

            if abs(t) > self.ROTATION:
                if t < -180 or t > 180:
                    t = -t
                self.rotate(-np.sign(t) * self.ROTATION)

            if abs(t) < 90:
                if speed_mod < ((self.DEACCELERATION+self.ENV_DEACCELERATION)
                                 *(dist/max(speed_mod,0.001)) + self.ENV_DEACCELERATION):
                    self.accelerate(self.ACCELERATION)

                elif speed_mod>1 and abs(true_ang) < 30:
                    self.accelerate(-self.DEACCELERATION)

            else:
                if speed_mod < ((self.DEACCELERATION+self.ENV_DEACCELERATION)
                                 *(dist/speed_mod) + self.ENV_DEACCELERATION):
                    self.accelerate(-self.DEACCELERATION)

                elif speed_mod>1 and true_ang < 30:
                    self.accelerate(self.ACCELERATION)

        else:
            self.to_do_list.remove(self.go)

    def go_to(self, obj=None, x=None, y=None):
        """
        go_to(obj=None, x=None, y=None)
        interface function. Stop after reaching the goal
        """
        self.assign_goal(obj=obj, x=x, y=y)
        self.to_do_list.append(self.go)

    def follow(self):
        """
        follow()
        follow the goal untill met stop_following()
        """
        if self.go not in self.to_do_list:
            self.to_do_list.append(self.go)

        if self.follow not in self.to_do_list:
            self.to_do_list.append(self.follow)

    def stop_following(self):
        """
        stop_following()
        Removes follow() and itself from to_do_list
        """
        self.to_do_list.remove(self.follow)
        self.to_do_list.remove(self.stop_following)

    def update(self):
        """Execute all functions in to_do_list if there is any goal"""
        # Excecute all todo dunctions if goal is player
        if self.goal in State.player_group:
            [x() for x in self.to_do_list]
        else:
            try:
                self.goal = State.player_group.sprites()[0]
            except:
                pass


class Agressor(ScriptMob):

    def __init__(self, image, x, y):

        super().__init__(image, x, y, 3)
        # Assign goal if
        try:
            self.assign_goal(State.player_group.sprites()[0])
        except:
            pass

        State.asteroids.add(self)
        self.look_dir = random.randint(0, 358)
        self.speed = [random.uniform(-3, 3), random.uniform(-3, 3)]


    def rush(self):
        dist = self.get_distance(self.goal)
        if dist > self.close_range:
            speed_mod = np.sqrt(self.speed[0]**2+self.speed[1]**2)
            # If speed is small, turn in the direction of goal,
            # otherwise, in the direction allowing greater speed vecror change
            if speed_mod < 1:
                t = self.look_dir - abs(self.get_aim_dir(self.goal))
            else:
                ang = np.arctan(self.speed[0]/self.speed[1])
                # Direction of motion
                spe = Object(blanc,
                             int(self.rect.centerx+30*np.sin(ang)
                                 *np.sign(self.speed[1])),
                             int(self.rect.centery+30*np.cos(ang)
                                 *np.sign(self.speed[1])))

                true_ang = self.get_aim_dir(self.goal) - self.get_aim_dir(spe)
                spe.kill()
                if true_ang < -180 or true_ang > 180:
                    true_ang = -360*np.sign(true_ang) + true_ang

                if true_ang < -90 or true_ang > 90:
                    t = self.get_aim_dir(self.goal)
                else:
                    t = self.get_aim_dir(self.goal) + true_ang

                # true_ang = self.get_aim_dir(self.goal) - true_ang
                t = self.look_dir - t
                if t > 360 or t < -360:
                    t += -360*np.sign(t)

            if abs(t) > self.ROTATION:
                if t < -180 or t > 180:
                    t = -t
                self.rotate(-np.sign(t) * self.ROTATION)

            if abs(t) < 90:
                self.accelerate(self.ACCELERATION)

            else:
                self.accelerate(self.ACCELERATION)

        if self.rush not in self.to_do_list:
            self.to_do_list.append(self.rush)


class Asteroid(Object, Moving, Vulnerable):

    noclip_count =0
    noclip_timer = 30

    velo_deviation = 1
    density = (1,2)

    def __init__(self, image, x, y, type, speed):

        super().__init__(pygame.transform.scale(image, (10*type, 10*type)),
                        x, y, width=type*10, height=type*10)

        Moving.__init__(self)
        Vulnerable.__init__(self, 1)

        self.type = type
        State.asteroids.add(self)
        self.image = pygame.transform.scale(image, (10*type, 10*type))
        self.speed = [speed[0] + random.uniform(-self.velo_deviation,
                                                 self.velo_deviation),
                      speed[1] + random.uniform(-self.velo_deviation,
                                                 self.velo_deviation)]
        self.look_dir = random.randint(-180, 180)
        self.hp = self.type * 2

        # movable.add(self)
        State.asteroids.add(self)
        self.rotate(0)

    def crash(self):
        if self.type >2:
            for x in range(6):
                FX_Track(particle, self.rect, 50,
                         look_dir=(random.randint(0,350)),
                         speed=[self.speed[0] + random.uniform(-1,1),
                                self.speed[1] + random.uniform(-1,1)],
                         color=(120,100,100,150))

        if self.type > 1:
            arr = []
            for i in range(random.choice(self.density)):

                i = Asteroid(self.image,
                    self.rect.centerx, self.rect.centery, self.type-1, self.speed)

                arr.append(i)

                if random.choice((1,0)):
                    i.speed[0] = -self.speed[0]
                else:
                    i.speed[1] = -self.speed[1]

            return arr
        self.kill()

    def update(self):
        self.noclip_count += 1
        if self.noclip_count > self.noclip_timer:
            self.noclip_count = 0
            State.noclip_asteroids.remove(self)


class Adv_Asteroid(Asteroid):

    def __init__(self, level, x, y, type, speed):

        super().__init__(asteroid_imgs[level-1], x, y, type, speed)
        self.level = level
        self.hp = State.asteroid_hps[level - 1] * self.type
        self.noclip_timer = State.asteroid_noclip_timers[level - 1]
        self.density = State.asteroid_densities[level - 1]
        self.velo_deviation = State.asteroid_velocity_deviations[level - 1]

    def damage(self, dmg, type=None, speed=None):

        self.hp += -max(0, dmg)

        rect = pygame.Rect(self.rect.x, self.rect.y,
                           self.type*10+10, self.type*10+10)

        if type != None:
            self.speed = [self.speed[0] + speed[0]*((type+1)/(self.type+1)),
                          self.speed[1] + speed[1]*((type+1)/(self.type+1))]

        if self.hp < 0:
            self.crash()
            return
            State.noclip_asteroids.add(self)

    def crash(self):

        if self.type >2:
            for x in range(6):
                FX_Track(particle, self.rect, random.randint(20,80),
                         look_dir=(random.randint(0,350)),
                         speed=[self.speed[0] + random.uniform(-1,1),
                                self.speed[1] + random.uniform(-1,1)],
                         color=(random.randint(90,200),100,100,150))

        if self.type > 1:
            arr = []
            for i in range(random.choice(self.density)):

                x = Adv_Asteroid(self.level, self.rect.centerx,
                                 self.rect.centery, self.type-1, self.speed)
                arr.append(i)

                if random.choice((1,0)):
                    x.speed[0] = -self.speed[0]
                else:
                    x.speed[1] = -self.speed[1]

                if random.choice((0,0,0,0,0,0,0,0,1)):
                    c = Agressor(bad_thing, self.rect.centerx, self.rect.centery)
                    c.remove(State.player_group)
                    c.rush()

        self.kill()


class Zone(pygame.sprite.Sprite, Vulnerable):

    def __init__(self, x, y, radius, hp, time):

        pygame.sprite.Sprite.__init__(self)
        Vulnerable.__init__(self, hp)
        self.radius = radius
        self.time_count = 0
        self.timer = time
        self.rect = pygame.Rect(x, y, 1, 1)


class Projectile(Object, Moving, Vulnerable):

    def __init__(self, bolt, x, y, distance, width=None, height=None):

        super().__init__(prj_imgs[bolt], x, y, width=width, height=height)
        Moving.__init__(self)
        Vulnerable.__init__(self, State.bolt_damage[bolt])

        self.speed_max = State.prj_speeds[bolt]
        self.timer = distance

        # movable.add(self)
        State.projectiles.add(self)
        State.time_dependent.add(self)

    def remove(self):
        self.kill()

    def damage(self, obj):
        buff = copy.copy(obj.hp)
        obj.damage(self.hp)
        self.hp += -buff
        if self.hp < 0:
            self.kill()
            self.hp = 0


class Missile(Projectile):

    # how often aim-updaing function to run
    compute_tempo = 5
    compute_count = 0

    def __init__(self, bolt, x, y):

        super().__init__(bolt + State.n_bolts, x, y, State.msl_distances[bolt])

        self.d_ang = State.msl_d_angs[bolt]
        self.d_speed = State.msl_d_speeds[bolt]
        self.max_speed = State.msl_max_speeds[bolt]
        self.hit_range = State.msl_hit_ranges[bolt]
        self.hp = State.bolt_damage[bolt + State.n_bolts]
        self.mod_speed = 0
        self.dist_prev = 500
        self.dist = None
        State.missiles.add(self)
        State.projectiles.remove(self)

        self.aim = self.lock_closest()

    def rotate_to_aim(self):

        aim_dir = self.get_aim_dir(self.aim)

        x = (self.look_dir - aim_dir)

        # if abs(x) < self.d_ang:
        #     pass
        if abs(x) > 180:
             self.rotate(self.d_ang*np.sign(x))

        else:
            self.rotate(-self.d_ang*np.sign(x))

    def lock_closest(self):
        arr = []
        for x in State.asteroids:
            arr.append(self.get_distance(x))
        if len(arr) > 0:
            return State.asteroids.sprites()[arr.index(min(arr))]
        else:
            return None

    def pursue(self):

        r = copy.copy(self.rect)

        # create engine particles
        FX_Track(particle, r, 40, look_dir=random.randint(0,358),
                        fading=[20,16], enlarging=[20,16],
                        color=(200,200,200,random.randint(40,130)),
                        speed=[random.uniform(-0.5,0.5), random.uniform(-0.5,0.5)])

        FX_Glow(r, 1, 2, 10, (255, 200, 125, 20))

        self.rotate_to_aim()
        self.mod_speed += self.d_speed

        # If missile is close enough to aim but fails to hit it (starts to get
        # further from aim), missile will detonate.
        self.dist = self.get_distance(self.aim)
        if self.dist > self.dist_prev and self.dist < self.hit_range:
            self.blow_up()
            return
        self.dist_prev = self.dist

        a1 = self.speed[0] + self.d_speed*np.cos(np.deg2rad(self.look_dir-90))
        if a1 < self.max_speed and a1 > -self.max_speed:
            self.speed[0] = a1
        else:
            self.speed[0] = self.max_speed*np.cos(np.deg2rad(self.look_dir-90))

        a2 = self.speed[1] + self.d_speed*np.sin(np.deg2rad(self.look_dir-90))
        if a2 < self.max_speed and a2 > -self.max_speed:
            self.speed[1] = a2
        else:
            self.speed[1] = self.max_speed*np.sin(np.deg2rad(self.look_dir-90))

    def update(self):

        if self.aim in State.asteroids:
            self.pursue()
        else:
            self.aim = self.lock_closest()

        self.compute_count += 1
        if self.compute_count > self.compute_tempo:
            self.compute_count = 0
            self.aim = self.lock_closest()

    def blow_up(self):

        x = Zone(self.rect.x, self.rect.y, self.hit_range, self.hp, 2)
        Funcs.FX_explosion(self.rect.centerx, self.rect.centery,
                           xpl=expN, radius=(60,60))
        State.hit_waves.add(x)
        State.time_dependent.add(x)
        self.kill()


class Animation(Object, Moving):
    '''
    Animation(images_arr, width, height, x, y,
              rand = False, finit = True, type = 0,
              hold_f = None, delay = 0)
    "rand" - if True, sets random direction of view. instances have
    lists of images that are updated with different rules depending
    on the "type".
     Types of animation are: standard (0), reverse(1), hold(2).
    "delay" - frames before displayed image is switched to
    next in types 0 and 1.
    "finit" - if True, animation will start over after reaching
    the end (or beginning in 1).
    "hold_f" - noumber of frame in "images_arr" animation will
    pause on in hold type animation.
    '''

    def __init__(self, images_arr, width, height, x, y, rand=False, finite=True,
                type=0, hold_f=None, delay=0):

        Object.__init__(self, images_arr[0], x, y, width=width, height=height)
        Moving.__init__(self)

        self.images_arr = images_arr
        if rand:
            self.look_dir = random.randint(-180, 180)
        else:
            self.look_dir = -90
        self.frames = len(images_arr)
        self.rotate(0)
        self.type = type
        self.delay = delay
        self.hold_frame = hold_f
        self.finite = finite

        self.frames_count = 0
        self.delay_count = 0

    def hold(self):

        if self.frames_count == self.hold_frame:
            pass
        else:
            if self.delay_count == self.delay:
                self.frames_count += 1

    def standard(self):

        if self.frames - self.frames_count == 1:
            if self.finite:
                self.kill()
            else:
                self.frames_count = 0

        else:
            if self.delay_count == self.delay:
                self.frames_count += 1

    def reverse(self):

        if self.frames_count == 0:
            if self.finite:
                self.kill()
            else:
                self.frames_count = len(self.images_arr)

        else:
            if self.delay_count == self.delay:
                self.frames_count += -1

    def update(self):

        self.image = self.images_arr[self.frames_count]
        self.rotate(0)

        if self.type == 0:
            self.standard()
        elif self.type == 1:
            self.reverse()
        else:
            self.hold()

        if self.delay_count == self.delay:
            self.delay_count = 0
        else:
            self.delay_count += 1


class Sector:

    def __init__(self, start:(int,int), type=0):
        """
        One map sector.
        :param start: top left coordinate of a sector
        :param type: different types of sectors have different probability of spawn for various things
        """
        self.all_objects = []
        # Generate chunks
        for x in range(State.N):
            for y in range(State.N):
                State.map_chuncks['{}{}-{}{}'.format(start[0], start[1], x, y)] = []


class Verse:

    def __init__(self):
        """
        Big map composed of many sectors. New sectors are generated based on big picture, so as big scale events.
        Generate:
        1. Resources  (with perlin noise)
        2. Fraction(s), their state  (with cell automata)
        3. Big events, like fleets, conflicts
        4. Sectors and details
        """


