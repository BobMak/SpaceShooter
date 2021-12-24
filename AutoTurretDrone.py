from AutoTurret import AutoTurret


class D_PreAim(AutoTurret):

    def __init__(self, image, radius, mounted_on, bolt_id, cooldown,
                 orbit_coef, d_ang, min, max, distance,
                 groups = None, look_dir = 0,
                 width = 24, height = 24, restriction = None):

        super().__init__(image, radius, mounted_on, bolt_id, cooldown,
                         groups, distance, look_dir,
                         width, height, restriction)
        self.mounted_on.turrets.remove(self)
        self.init_orbit(orbit_coef, d_ang, min, max, distance)

