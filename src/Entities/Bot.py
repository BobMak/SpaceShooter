from queue import Queue

from Core.Mechanics import *
from Ships.Ship import Ship


class Bot(Ship):

    def __init__(self, image, x, y, picked_ship='tick', state=None):
        """
        A bot is a ship that can move and shoot.
        it has an action queue that contains actions to execute.
        An action, for example is to chase a player. Actions take multiple frames
        to execute. All action functions have to return a boolean that indicates
        if the action is finished.
        After an action is finished, the next action is poped from the queue.
        :param image:
        :param x:
        :param y:
        :param picked_ship:
        :param state:
        """
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
                         env_friction=State.ship_types[picked_ship]['env_deacceleration'],
                         state=state
                         )
        state.script_mob_group.add(self)
        self.close_range = 20
        self.action = None
        self.action_queue = Queue()

    def update(self):
        """Execute all functions in to_do_list if there is any goal"""
        if not self.action and not self.action_queue.empty():
            self.action = self.action_queue.get()
        elif self.action:
            if self.action():
                self.action = None

