import random as r

import Map
import State
# import Ships


def spawnPlayer(n):
    sector_x, sector_y = r.randint(0, n), r.randint(0, n)


if __name__ == "__main__":
    v = Map.Verse()
    for x in range(v.N):
        for y in range(v.N):
            print(v.sectors[y][x], end=' ')
        print()
