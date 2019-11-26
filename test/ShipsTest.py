import unittest
import Ships


class TestShips(unittest.TestCase):
    def setUp(self) -> None:
        raise NotImplementedError()

    def tearDown(self) -> None:
        raise NotImplementedError()

    def testShipGeneration(self):
        ship = Ships.Ship()


if __name__ == '__main__':
    unittest.main()
