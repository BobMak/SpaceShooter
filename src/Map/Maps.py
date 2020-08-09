import pyglet as pg
import random as r
import pickle
import os

from Core import Noise


# A part of map for which events are computed on a more granular level.
# Includes several sectors that are closest to a player.
class Window:
    def __init__(self, sectors, w, h):
        # Displayed map x and y
        self.width, self.height = w, h
        # coordinates of the highest left point of the screen
        # with respect to the leftmost sector. These are changed when player
        # moves in direction outside of displayed region
        self.base_x, self.base_y = 0, 0
        self.current_sector = sectors[0][0]
        self.sectors_on_screen = [self.current_sector]
        # Player function
        self.focus = None  # Object that the player is looking at
        self._available = []  # can control these
        self._schemas = []  # can build these with proper equipment

    def addAvailable(self, object):
        self._available.append(object)

    def add_sector(self):
        pass
    def rm_sector(self):
        pass

    def move(self, x, y):
        self.base_x, self.base_y = x, y

    def followFocus(self):
        self.move(self.focus.rect[0] - self.width  // 2 + self.focus.speed[0]*10,
                  self.focus.rect[1] - self.height // 2 + self.focus.speed[1]*10)

    def draw(self):
        self.current_sector.bgImage.blit(0, 0,
                                         width=self.current_sector.LENGTH,
                                         height=self.current_sector.LENGTH)


# Contains all event groups that objects can subscribe to.
class Sector:
    def __init__(self, id:(int,int), type=0):
        """
        :param start: top left Verse coordinate of a sector (coordinates / LENGTH)
            e.g. (3000, 3000) -> (1,1)
        :param type:
        """
        print("Generating new sector", id)
        self.id          = id
        self.type        = r.randint(0, 5)
        self.LENGTH      = 3000  # square 3000x3000
        self.all_objects = []
        self.updateable  = []
        self.bgImage = Noise.getNoiseImage(size=400, persistance=0.5, depth=8)

    def __new__(cls, id=None, *args, **kwargs):
        if str(id).replace(' ', '')[1:-1] + '.pkl' in os.listdir('../data/map'):
            with open('../data/map/' + id + '.pkl', 'rb') as f:
                inst = pickle.load(f)
            if not isinstance(inst, cls):
                raise TypeError('Unpickled object is not of type {}'.format(cls))
        else:
            inst = super(Sector, cls).__new__(cls, *args, **kwargs)
        return inst

    def __str__(self):
        return "Sector "+str(self.type)

    def save(self):
        with open('../data/map/' + self.id + '.pkl', 'wb') as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)


class Verse:
    def __init__(self):
        """Big map composed of many sectors. New sectors are generated based on big picture, so as big scale events.
        Generate:
        1. Resources
        2. Ships, obejcts
        3. Sectors and details
        """
        self.N = 2  # verse sector size
        self.sectors = [ [ Sector((x,y)) for y in range(self.N) ] for x in range(self.N)]
        # Generate sectors

    def loadSector(self, id):
        if str(id).replace(' ', '')[1:-1]+'.pkl' in os.listdir('../map'):
            with open(id+'.pkl', 'wb') as f:
                r = pickle.load(f)
        else:
            r = Sector(id)
        return r


