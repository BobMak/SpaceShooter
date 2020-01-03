import pygame as pg
import random as r
import pickle
import os


# A part of map for which events are computed on a more granular level.
# Includes several sectors that are closest to a player.
class Window:
    def __init__(self, sectors):
        # Displayed map x and y
        self.width, self.height = 1200, 1000
        # coordinates of the highest left point of the screen
        # with respect to the leftmost sector. These are changed when player
        # moves in direction outside of displayed region
        self.base_x, self.base_y = 0, 0
        self.current_sector = sectors[r.randint(0, 4)][r.randint(0, 4)]
        self.sectors_on_screen = [self.current_sector]
        self.interface = pg.sprite.Group()  # Game interface objects
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
        print('moved to', x, y)

    def move_movable(self):
        for sector in self.sectors_on_screen:
            for object in sector.movable:
                object.modify_position()


# Contains all event groups that objects can subscribe to.
# Some of most important ones are collision groups. I hope to gain speed by
# computing collisions only for objects in the same sector.
class Sector:
    def __init__(self, start:(int,int), type=0):
        """
        :param start: top left Verse coordinate of a sector (coordinates / LENGTH)
            e.g. (3000, 3000) -> (1,1)
        :param type: different types of sectors have different probability of spawn for various things
        """
        self.    verse_crds = start
        self.          type = r.randint(0, 5)
        self.        LENGTH = 3000  # square 3000x3000
        self.   all_objects = []
        self.    updateable = []
        self.       movable = pg.sprite.Group()
        self.   projectiles = pg.sprite.Group()
        self.time_dependent = pg.sprite.Group()
        self.  player_group = pg.sprite.Group()
        self.          glow = pg.sprite.Group()
        self.       effects = pg.sprite.Group()
        self.       visible = pg.sprite.Group()

    def __str__(self):
        return "Sector "+str(self.type)


class Verse:
    def __init__(self):
        """Big map composed of many sectors. New sectors are generated based on big picture, so as big scale events.
        Generate:
        1. Resources
        2. Faction(s), their state
        3. Big events, fleets, conflicts
        4. Sectors and details
        """
        self.N = 5  # verse sector dimensions
        self.sectors = [ [ Sector((x,y)) for y in range(self.N) ] for x in range(self.N)]
        # Generate sectors

    def loadSector(self, id):
        if str(id).replace(' ', '')[1:-1]+'.pkl' in os.listdir('../map'):
            with open(id+'.pkl', 'wb') as f:
                r = pickle.load(f)
        else:
            r = Sector(id)
        return r


