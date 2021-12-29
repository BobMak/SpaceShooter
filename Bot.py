from Mechanics import *
from Ship import Ship


class Bot(Ship):

    def __init__(self, image, x, y, picked_ship='tick'):

        super().__init__(image, x, y,
                         bolt=State.ship_types[picked_ship]['bolt'],
                         missile=State.ship_types[picked_ship]['missile'],
                         hp=State.ship_types[picked_ship]['hull'],
                         shield=State.ship_types[picked_ship]['shields'],
                         rotation_rate=State.ship_types[picked_ship]['rotation_rate'],
                         acceleration=State.ship_types[picked_ship]['acceleration'],
                         max_acceleration_reserve=State.ship_types[picked_ship]['acceleration_tank'],
                         acceleration_burn_rate=State.ship_types[picked_ship]['acceleration_burn_rate'],
                         acceleration_reserve_regeneration=State.ship_types[picked_ship][
                             'acceleration_reserve_regeneration'],
                         deacceleration=State.ship_types[picked_ship]['deacceleration'],
                         env_deacceleration=State.ship_types[picked_ship]['env_deacceleration'],
                         )
        State.script_mob_group.add(self)
        self.close_range = 20
        self.goal = None
        self.to_do_list = []

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
            self.goal = GObject(blanc, x, y)
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
                spe = GObject(blanc,
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
                    self._accelerate(self.ACCELERATION)

                elif speed_mod>1 and abs(true_ang) < 30:
                    self._accelerate(-self.DEACCELERATION)

            else:
                if speed_mod < ((self.DEACCELERATION+self.ENV_DEACCELERATION)
                                 *(dist/speed_mod) + self.ENV_DEACCELERATION):
                    self._accelerate(-self.DEACCELERATION)

                elif speed_mod>1 and true_ang < 30:
                    self._accelerate(self.ACCELERATION)

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
        # Excecute all to-dos if goal is player
        if self.goal in State.player_group:
            for x in self.to_do_list:
                try:
                    x()
                except:
                    pass
        else:
            try:
                self.goal = State.player_group.sprites()[0]
            except:
                pass
