import pygame as pg
import threading

import unittest
from Ships import Ships
from Core import Scripts as Sc, State as St


class TestShips(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = pg.time.Clock()
        self.graph = Sc.Graphics()
        St.graphics_thread = threading.Thread(target=St.graphics.screen_redraw)
        St.graphics_thread.start()

    def tearDown(self) -> None:
        St.graphics_thread.stop()
        exit()

    def shipsHaveBasics(self):
        for x in range(100):
            s = Ships.ShipGenerator.generate_test()
            self.assertIsNot(s.maxSpeed, 0)


if __name__ == '__main__':
    unittest.main()
