import pygame as pg
import threading

import unittest
import Ships
import Scripts as Sc
import State as St


class TestShips(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = pg.time.Clock()
        self.graph = Sc.Graphics()
        St.graphics_thread = threading.Thread(target=St.graphics.screen_redraw)
        St.graphics_thread.start()

    def tearDown(self) -> None:
        St.graphics_thread.stop()
        exit()

    def testShipGeneration(self):
        s = Ships.ShipGenerator.generate_test()


if __name__ == '__main__':
    unittest.main()
