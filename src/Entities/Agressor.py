from Core import Items
from Utils import get_angle
from Core.Mechanics import *
from Entities.Bot import Bot


class Agressor(Bot):
    def __init__(self, image, x, y, state=None, **kwargs):
        super().__init__(image, x, y, state=state, **kwargs)
        # Assign goal if
        try:
            self.assign_goal(state.player_group.sprites()[0])
        except:
            pass

        state.asteroids.add(self)
        self.look_dir = random.randint(0, 358)
        self.v = [random.uniform(-3, 3), random.uniform(-3, 3)]
        self.type = 2

    def rush(self):
        dist = self.get_distance(self.goal)
        if dist > self.close_range:
            velocity_mod = np.sqrt(self.v[0]**2+self.v[1]**2)
            # If speed is small, turn in the direction of goal,
            # otherwise, in the direction allowing greater speed vecror change
            if velocity_mod < 1:
                t = self.look_dir - get_angle(self.rect.center, self.goal.rect.center)
            else:
                ang = np.arctan(self.v[0]/self.v[1])
                # Direction of motion
                spe = (self.rect.centerx+30*np.sin(ang)*np.sign(self.v[1]),
                       self.rect.centery+30*np.cos(ang)*np.sign(self.v[1]))

                true_ang = get_angle(self.rect.center, self.goal.rect.center) - get_angle(self.rect.center, spe)
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

            if abs(t) > self.rotation_rate:
                if t < -180 or t > 180:
                    t = -t
                self.apply_force_angular(-np.sign(t) * self.rotation_rate)

            if abs(t) < 90:
                self.accelerate(self.acceleration)

            else:
                self.accelerate(self.acceleration)

        if self.rush not in self.to_do_list:
            self.to_do_list.append(self.rush)

    def destroy(self):
        super().kill()
        Items.MissileItem(self.rect.centerx, self.rect.centery, 1, state=self.state)

    def __str__(self):
        return "Agressor" + super().__str__()
