import copy
import random
import threading

import numba
import numpy as np

import Assets
import State
from Assets import *
from Funcs import dict_hash


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
    def __init__(self,
                 env_deacceleration=0.1,
                 speed=(0.0, 0.0),
                 look_dir=0.0,
                 ):
        self.env_deacceleration = env_deacceleration
        self.look_dir = look_dir
        self.speed = speed
        self.position = [self.rect.x, self.rect.y]
        State.movable.add(self)

    def modify_position(self):
        "modifyes position with respect to <1 values of acceleration"
        self.position[0] += self.speed[0]
        self.position[1] += self.speed[1]

        self.rect = pygame.Rect(self.position[0], self.position[1],
                                self.rect.width, self.rect.height)

    def slow_down(self):
        # self.speed[0] += (self.env_deacceleration
        #                   *abs(np.cos(np.deg2rad(self.look_dir-90.0)))
        #                   *-np.sign(self.speed[0]))
        #
        # self.speed[1] += (self.env_deacceleration
        #                   *abs(np.sin(np.deg2rad(self.look_dir-90.0)))
        #                   *-np.sign(self.speed[1]))
        self.speed = (self.speed[0] + (self.env_deacceleration
                          *abs(np.cos(np.deg2rad(self.look_dir-90.0)))
                          *-np.sign(self.speed[0])),
                      self.speed[1] + (self.env_deacceleration
                          *abs(np.sin(np.deg2rad(self.look_dir-90.0)))
                          *-np.sign(self.speed[1])))

    def _accelerate(self, temp):
        self.speed = (self.speed[0] + temp*np.cos(np.deg2rad(self.look_dir-90.0)),
                      self.speed[1] + temp*np.sin(np.deg2rad(self.look_dir-90.0)))

    def bound_pass(self):
        if (self.position[0] < -self.rect.width
                or self.position[0] > WIDTH):
            # self.rect = self.rect.move((-(Assets.WIDTH + self.rect.width) * np.sign(self.rect.centerx)), 0)
            # self.rect.centerx += -(width + self.rect.width) * np.sign(self.rect.centerx)
            self.position[0] += -(WIDTH + self.rect.width) * np.sign(self.rect.x)
            # except: pass

        if (self.position[1] < -self.rect.height
                or self.position[1] > HEIGHT):
            # self.rect = self.rect.move(0, (-(height + self.rect.width) * np.sign(self.rect.centery)))
            self.position[1] += -(HEIGHT + self.rect.height) * np.sign(self.rect.y)
            # except: pass

    @staticmethod
    def move_movable():
        for object in State.movable:
            # modify position to avoid loss of <1 values when moving
            object.modify_position()


class FX(pygame.sprite.Sprite, Moving):

    def __init__(self, rect, duration):

        pygame.sprite.Sprite.__init__(self)

        self.timer = duration
        self.time_count = 0
        self.rect = rect

        # Requires rect to already be there
        Moving.__init__(self)

        State.time_dependent.add(self)

    # this stub is required to be able to use the class in the sprite group
    def draw_rotating(self):
        pass


class FX_Glow(FX):
    """
    FX_Glow(rect, duration, radius, length, color, speed=(0,0))
    """
    def __init__(self, rect, duration, radius, length, color, speed=(0,0)):

        FX.__init__(self, rect, duration)
        self.radius = radius
        self.color = color
        self.length = length
        self.speed = speed
        State.glow.add(self)

    def draw_rotating(self):
        """
        drawing funcition
        """
        for x in range(self.length):
            pygame.gfxdraw.filled_circle(State.screen, self.rect.centerx,
                                         self.rect.centery, self.radius+x,
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
                fading=None, enlarging=None, color=None,
                look_dir=None, speed=None):
        '''density - [0-1]'''
        FX.__init__(self, rect, duration)

        self.updates = []
        self.fading_count = 0
        self.fading_sum = 0

        self.look_dir = 0

        self.enlarging_count = 0
        self.enlarging_summ = 1

        self.image = pygame.transform.scale(image, (rect.width, rect.height))

        if color != None:
            self.image.fill((color[0], color[1], color[2], color[3]),
                            None, pygame.BLEND_RGBA_MULT)

        if look_dir != None:
            self.look_dir = look_dir
            self.rotated_image = pygame.transform.rotate(self.image,
                                                        -self.look_dir)
            self.image = pygame.transform.rotate(self.image,
                                                -self.look_dir)
            self.rotated_image_base = pygame.transform.rotate(self.image,
                                                             -self.look_dir)
        else:
            self.rotated_image = copy.copy(self.image)

        if fading != None:
            self.fading = fading[0]
            self.fading_tempo = fading[1]
            self.updates.append(self.fade)

        if enlarging != None:
            self.enlarging = enlarging[0]
            self.enlarging_tempo = enlarging[1]
            self.updates.append(self.enlarge)

        if speed != None:
            self.speed = speed

        State.effects.add(self)

    def enlarge(self):
        self.enlarging_count += 1
        if self.enlarging_count > self.enlarging_tempo:
            self.enlarging_count = 0
            self.enlarging_summ += self.enlarging
            if self.enlarging_summ > 250:
                self.kill()
                return
            self.rotated_image = pygame.transform.scale(self.rotated_image,
                                                (self.rect.width+self.enlarging,
                                                self.rect.height+self.enlarging))

    def fade(self):
        self.fading_count += 1
        if self.fading_count > self.fading_tempo:
            self.fading_count = 0

            self.fading_sum += self.fading

            if self.fading_sum > 230:
                self.kill()
                return
            self.rotated_image_base.fill((255, 255, 255, 255-self.fading_sum),
                                         None, pygame.BLEND_RGBA_MULT)

    def update(self):
        self.rotated_image = copy.copy(self.rotated_image_base)
        for f in self.updates:
            f()

    def draw_rotating(self):
        rect = self.rotated_image.get_rect()
        rect.center = (self.rect.center)
        State.screen.blit(self.rotated_image, rect)


class GObject(pygame.sprite.Sprite):
    '''GObject(image, x, y, width=None, height=None)'''

    def __init__(self, image, x, y, width=None, height=None):
        pygame.sprite.Sprite.__init__(self)

        self.look_dir = 0.0
        self.rotated_image = 0
        self.rotated_rect = 0
        self.radius = None
        self.dmg = None
        self.time_count = 0
        self.timer = 0
        if width != None:
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
                    - (obj.rect.centerx + x*(WIDTH+obj.rect.width)))
                b = (self.rect.centery
                    - (obj.rect.centery + y*(HEIGHT+obj.rect.height)))
                dist = np.sqrt(a**2 + b**2)
                all_directions_distances.append(dist)

        return min(all_directions_distances)

    def get_closest_aim_dir(self, aim):
        """
        returns the angle of closest position of aim with respect to looped map.
        """
        all_directions_distances = []
        for x in range(-1, 2):
            for y in range(-1, 2):
                a = (self.rect.centerx
                    - (aim.rect.centerx + x*(WIDTH+aim.rect.width)))
                b = (self.rect.centery
                    - (aim.rect.centery + y*(HEIGHT+aim.rect.height)))

                dist = np.sqrt(a**2 + b**2)
                all_directions_distances.append(dist)

        best = all_directions_distances.index(min(all_directions_distances))

        if best < 3: x = -1
        elif best > 5: x = 1
        else: x = 0
        if (best+1)%3 == 0: y = 1
        elif best in [1, 3, 6]: y = 0
        else: y = -1
        a = aim.rect.centerx + x*(WIDTH + aim.rect.width)
        b = aim.rect.centery + y*(HEIGHT + aim.rect.height)
        aim = GObject(blanc, a, b)
        return self.get_aim_dir(aim)

    def draw_rotating(self):
        rect = self.rotated_image.get_rect()
        rect.center = (self.rect.center)
        State.screen.blit(self.rotated_image, rect)


class Colliding(pygame.sprite.Sprite, Moving):
    '''
    Colliding(width, height, distance, angle, source)
    Smaller collision rect container for more complex forms.
    should be rotated with source object with "orbit_rotate"
    '''

    def __init__(self, width, height, distance, angle, source):

        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect((source.rect.x
                               + (np.deg2rad(np.cos(angle)) * distance)),
                                (source.rect.y
                               + np.deg2rad(np.sin(angle)) * distance),
                                 width, height)

        self.speed = source.speed
        self.angle = angle
        self.source = source
        self.distance = distance
        self.orbit_ang = angle

        Moving.__init__(self)


class Animation(GObject, Moving):
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
    "hold_f" - noumber of frame in "images_arr" animatino will
    pause on in hold type animation.
    '''

    def __init__(self, images_arr, width, height, x, y, rand=False, finit=True,
                type=0, hold_f=None, delay=0):
        super().__init__(images_arr[0], x, y, width=width, height=height)
        Moving.__init__(self)
        self.frames_count = 0
        self.delay_count = 0
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
        self.finit = finit
        # movable.add(self)

    def hold(self):
        if self.frames_count == self.hold_frame:
            pass
        else:
            if self.delay_count == self.delay:
                self.frames_count += 1

    def standard(self):
        if self.frames - self.frames_count == 1:
            if self.finit:
                self.kill()
            else:
                self.frames_count = 0

        else:
            if self.delay_count == self.delay:
                self.frames_count += 1

    def reverse(self):
        if self.frames_count == 0:
            if self.finit:
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

    # this method shall be called when we know the properties of the required explosion
    @staticmethod
    def prepareExplosions(**params):
        prm_hash = dict_hash(params)
        def _work():
            if prm_hash not in State.buff_explosions:
                State.buff_explosions[prm_hash] = []
                for i in range(5):
                    animation = Animation.generateExplosionAnimation(**params)
                    State.buff_explosions[prm_hash].append(animation)

        threading.Thread(target=_work).start()

    @staticmethod
    def generateExplosionAnimation(diameter=30, n_frames=30,
                                   decay_rgb=(0, 6, 9),
                                   start_rgb=(255, 255, 255),
                                   spawn_points=230):
        """
        generates a set of explosion animations using cellular automata
        """
        animation = []
        img_buffer = np.zeros((diameter, diameter, 3), dtype=np.int16)
        # generate an initial circle in the center proporional to damage
        img_buffer[int(diameter / 2), int(diameter / 2)] = start_rgb
        for i in range(int(3)):
            for j in range(int(3)):
                img_buffer[int(diameter / 2) + i, int(diameter / 2) + j] = start_rgb
                img_buffer[int(diameter / 2) + i, int(diameter / 2) - j] = start_rgb
                img_buffer[int(diameter / 2) - i, int(diameter / 2) + j] = start_rgb
                img_buffer[int(diameter / 2) - i, int(diameter / 2) - j] = start_rgb

        # rule set
        @numba.jit(nopython=True)
        def automata(x, y, img_buffer):
            # if pixel has 3 or more neighbors that are > 200, it will be set to their average
            # when vlaue is != 0, it will decay by a random amount
            if img_buffer[x, y, 0] != 0:
                # make sure the decay stops the explosion before it reaches the boundary within the given n_frames
                # or faster
                v = (255 + diameter) // diameter
                _decay = random.randint(int(v), int(v) + 9)
                # decay = random.randint(int(diameter/n_frames),int(diameter/n_frames + 10))
                decay = np.array((_decay + decay_rgb[0], _decay + decay_rgb[1], _decay + decay_rgb[2]), dtype=np.int16)
                img_buffer[x, y] = img_buffer[x, y] - decay
            # when the value is 0, it will become 255 if it has 3 neighbors that are > 200
            else:
                count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        try:
                            count += img_buffer[x + i, y + j, 0] > spawn_points
                        except:
                            pass
                if count >= 3:
                    # the further from center, the less is the probabilit of being set to 255
                    if random.random() > (abs(x - diameter / 2) + abs(y - diameter / 2)) / diameter:
                        img_buffer[x, y] = start_rgb

        for i in range(diameter):
            # apply cellular automata
            for x in numba.prange(diameter):
                for y in numba.prange(diameter):
                    automata(x, y, img_buffer)

            # create animation frame
            img_buffer[img_buffer < 5] = 0
            surf = pygame.surfarray.make_surface(img_buffer)
            # stop early if all values are 1
            if np.all(img_buffer == 0):
                break
            surf.set_colorkey((0, 0, 0), pygame.RLEACCEL)
            surf = pygame.transform.scale(surf, (int(diameter * 3), int(diameter * 3)))
            animation.append(surf)

        # downsample to a specified size if needed
        final = []
        if n_frames < len(animation):
            for i in range(n_frames):
                final.append(animation[int(i*len(animation)/n_frames)])
        else:
            final = animation

        return final

    @staticmethod
    def FX_explosion(x, y, xpl=Assets.expl, radius=(30, 30), randdir=True):
        obj = Animation(xpl, radius[0], radius[1], x, y, randdir)
        obj.rect.centerx += - 20
        obj.rect.centery += - 20
        State.effects.add(obj)
        return obj

    @staticmethod
    def FX_engine_mark(source):
        object = Animation(Assets.engi, 10, 10,
                           source.rect.centerx
                           + source.rect.height//2
                           * np.cos(np.deg2rad(source.look_dir + 90))
                           ,
                           source.rect.centery
                           + source.rect.height//2
                           * np.sin(np.deg2rad(source.look_dir + 90))
                           )
        object.look_dir = source.look_dir
        object.rotate(0)
        object.speed = source.speed

        State.effects.add(object)