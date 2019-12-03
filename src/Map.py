import pygame as pg
import random as r
import sys
import pickle
import os

import State as St

if 'Classes' not in sys.modules:
    import Classes


class Window:
    def __int__(self) -> None:
        """ A singleton map for which events are computed. Includes several
        sectors that are closest to a player.
        The class should translate respective coordinates of all objects
        from sectors to a player's screen.
        """
        # Displayed map x and y. This can change on zoom in/out
        self.width, self.height = 1200, 1000
        # coordinates of the highest left point of the screen
        # with respect to the leftmost sector. These are changed when player
        # moves in direction outside of displayed region
        self.base_x, self.base_y = 0, 0
        self.current_sector = None
        self.sectors = []
        self.interface = pg.sprite.Group()  # Game interface objects
        St.window = self

    def add_sector(self):
        pass
    def rm_sector(self):
        pass

    def reposition(self, x, y):
        self.base_x, self.base_y = x, y


class Sector:
    def __init__(self, start:(int,int), type=0):
        """One map sector. Contains all event groups that objects can subscribe to.
        Some of most important ones are collision groups. I hope to gain speed by
        computing collisions only for objects in the same sector.
        :param start: top left Verse coordinate of a sector (coordinates / LENGTH)
            e.g. (3000, 3000) -> (1,1)
        :param type: different types of sectors have different probability of spawn for various things
        """
        self.    verse_crds = start
        self.          type = r.randint(0, 5)
        self.        LENGTH = 3000  # square 3000x3000
        self.   all_objects = []
        self.       movable = pg.sprite.Group()
        self.   projectiles = pg.sprite.Group()
        self.time_dependent = pg.sprite.Group()
        self.  player_group = pg.sprite.Group()
        self.          glow = pg.sprite.Group()
        self.       effects = pg.sprite.Group()

    def __str__(self):
        return str(self.type)


class Verse:
    def __init__(self):
        """Big map composed of many sectors. New sectors are generated based on big picture, so as big scale events.
        Generate:
        1. Resources
        2. Fraction(s), their state
        3. Big events, like fleets, conflicts
        4. Sectors and details
        """
        if 'player.pkl' in os.listdir('../data'):
            with open('player.pkl', 'rb') as f:
                St.player = pickle.load(f)
        else:
            print('No player file found. Making new one')
            St.player = Classes.Player()
        self.N = 5  # verse sector dimensions
        self.sectors = [ [ Sector((x,y)) for y in range(self.N) ] for x in range(self.N)]
        # Generate sectors

        St.verse = self

    def loadSector(self, id):
        if str(id).replace(' ', '')[1:-1]+'.pkl' in os.listdir('../map'):
            with open(id+'.pkl', 'wb') as f:
                r = pickle.load(f)
        else:
            r = Sector(id)
        return r

