from Mechanics import *


class Mounted(GObject):
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
