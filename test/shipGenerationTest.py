import numpy as np
import random
import pygame as pg
from pygame import gfxdraw as gfx
import time
import copy

import Utils

screen_size=500


class Point:
    def __init__(self, x, y, color=(0,255,0, 100)):
        self.x = x
        self.y = y
        self.cns=[]
        self.color = color

    def getX(self):
        "For drawing"
        return (self.x + screen_size//4)*2

    def getY(self):
        "For drawing"
        return (self.y + screen_size//4)*2

    def connect(self, point):
        self.cns.append(point)
        return True

    def getDist(self, point):
        return np.sqrt((self.x-point.x)**2 + (self.y-point.y)**2)

    def getClosest(self, points):
        if self in points:
            points.remove(self)
        points.sort(key=lambda a: self.getDist(a))
        return points


def generate_skeleton_torus(size, radius, radius_var, symmetry=True):
    points = []
    size = size // 2 if symmetry else size
    for point in range(size):
        angle = random.random() * 2 * np.pi
        x = np.cos(angle) * radius + random.uniform(-radius_var, radius_var)
        y = np.sin(angle) * radius + random.uniform(-radius_var, radius_var)
        points.append((x,y))
        if symmetry:
            points.append((-x, y))
    return points


def generate_skeleton_triangle(size, radius, radius_var, symmetry=True, ang=1.0):
    points = []
    size = size//2 if symmetry else size
    for point in range(size):
        x = random.uniform(-radius, radius) + random.uniform(-radius_var, radius_var)
        y = radius - (ang * np.absolute(x)) + random.uniform(-radius_var, radius_var)
        points.append(Point(x, -y))
        if symmetry:
            points.append(Point(-x, -y))
    for p in points:
        all_points = copy.deepcopy(points)
        all_points.pop(points.index(p))
        for idx in range(3):
            closest = p.getClosest(all_points)[0]
            p.connect(closest)
            all_points.remove(closest)
    return points


def generate_tree(size, dist=18, ddist=6, dang=60, branching=0.5, clusterRad=25, symmetry=True):
    """:param size: 10x10 pixel blocks n
    :param branching: probability starting to grow from a random previous block
    """
    points = []
    centers = []
    x, y = 0, 0
    ang = 0
    points.append(Point(x,y))
    if symmetry:
        size=size//2  # will copy left side points to the right
    for point in range(size):
        # start growing from different point
        if random.random() < branching:
            newPivot = random.choice(points)
            x, y = newPivot.x, newPivot.y
        attempts=0
        # Try to generate a new point that is n pixels away from any other point.
        while True:
            _dist = random.normalvariate(dist, ddist)  # a random distance to a new point
            ang += random.uniform(-dang, dang)         # new angle shouldn't change too fast
            x += _dist * np.cos(np.deg2rad(ang))
            y += _dist * np.sin(np.deg2rad(ang))
            p = Point(x, y)
            if p.getClosest(points)[0].getDist(p) > 10:
                break
            elif attempts > 10:
                newPivot = random.choice(points)
                x, y = newPivot.x, newPivot.y
                attempts = 0
            attempts+=1
        points.append(p)
        if symmetry:
            points.append(Point(-x, y))
    # do k-means to create centers and connect all module centers
    cds = {}
    # pointsTo = copy.deepcopy(points)
    # # Add new centroids while all haven't been covered
    # n_cluster = 0
    # n_iter = 0
    # while len(pointsTo)>0:
    #     n_cluster += 1
    #     centr = Point(random.randint(-50,50), random.randint(-50,50))
    #     prev = np.array([100, 100])
    #     curr = np.array([0, 0])
    #     while np.linalg.norm(prev - curr)>2:
    #         n_iter+=1
    #         print('cluster {} iter {}'.format(n_cluster, n_iter), np.linalg.norm(prev - curr))
    #         ps =  centr.getClosest(pointsTo)
    #         avg_x = sum([p.x for p in ps]) // len(ps)
    #         avg_y = sum([p.y for p in ps]) // len(ps)
    #         centr.x = avg_x
    #         centr.y = avg_y
    #         prev = curr
    #         curr = np.array([avg_x, avg_y])
    #         if centr in cds:
    #             cds[centr].extend(centr.getClosest(pointsTo)[:5])
    #         else:
    #             cds[centr] = centr.getClosest(pointsTo)[:5]
    #     for p in centr.getClosest(pointsTo):
    #         if p.getDist(centr) <= centr.getClosest(pointsTo)[min(len(pointsTo)-1, 3)].getDist(centr):
    #             pointsTo.remove(p)
    _hull_points = copy.deepcopy(points)
    # Add hull
    hull = []  # Layers of hulls [ [ (p1, p2), ... ], ... ]
    _layer=0
    while len(_hull_points):  # add new layers while there are points
        subHull = []
        hull.append(subHull)
        _hull_points.sort(key=lambda p: p.x)
        print('layer', _layer,'points left', len(_hull_points))
        _layer+=1
        p1 = _hull_points[0]
        while True:
            p2 = random.choice(_hull_points)
            for p in _hull_points:
                if Utils.orientation(p1, p2, p) == 1:
                    p2 = p
            if (p1, p2) in subHull or (p2, p1) in subHull:  # Exit condition - lines form a cycle
                break
            subHull.append((p1, p2))
            p1 = p2
        for pair in subHull:  # remove points from
            try:_hull_points.remove(pair[0])
            except: pass
            try:_hull_points.remove(pair[1])
            except: pass
    return points, cds, hull


def shrink(hull: [[(Point, Point)]], a):
    """given a hull with n layers and a parameter A, replace connections in
    outer layers with connections to inner layers.
    Replace a line in the outer layer with two lines going to an inner layer
    :param hull: set of layers"""
    outer = hull[0]
    inner = [l for subhull in hull[1:] for l in subhull]  # get lines from list of lists of lines
    for idx in range(a):
        idx=idx*2
        _outer_points = [p for l in outer for p in l]
        _inner_points = [p for l in inner for p in l]
        if idx >= len(outer):
            break
        p1, p2 = outer[idx]  # outer edge to be removed
        # corresponding line on the other side
        inv_p1 = Point(-p1.x, p1.y).getClosest(_outer_points)[0]  # [x for line in outer for x in line]
        inv_p2 = Point(-p2.x, p2.y).getClosest(_outer_points)[0]  # get the inverse side of that
        # find closest line from the inner edge
        new_p1 = p1.getClosest(_inner_points)[0]
        new_p2 = p2.getClosest(_inner_points)[0]
        if (inv_p2, inv_p1) in outer:
            inv_idx = outer.index((inv_p2, inv_p1))
        elif (inv_p1, inv_p2) in outer:
            inv_idx = outer.index((inv_p1, inv_p2))
        else:
            print('no inverse point')
            continue
        # a new opposite side line in the inner layer
        new_inv_p1 = Point(-new_p1.x, new_p1.y).getClosest(_inner_points)[0]
        new_inv_p2 = Point(-new_p2.x, new_p2.y).getClosest(_inner_points)[0]
        del outer[idx]
        del outer[inv_idx-1]
        p1.color, new_p1.color = (255, 0, 0, 150), (255, 0, 0, 150)
        p2.color, new_p2.color = (255, 0, 0, 150), (255, 0, 0, 150)
        inv_p1.color, new_inv_p2.color = (255, 0, 0, 150), (255, 0, 0, 150)
        inv_p2.color, new_inv_p2.color = (255, 0, 0, 150), (255, 0, 0, 150)
        outer.extend([(inv_p1, new_inv_p1), (inv_p2, new_inv_p2)])
        outer.extend([(p1, new_p1), (p2, new_p2)])
    return hull


if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((500, 500))
    random.seed(145)
    while 1:
        sim = random.choice([True, False])  # symmetrical or asymmetrical
        size = 100
        radius = size*4
        radius_diff = 5
        ang = 0.5
        # for p in generate_skeleton_triangle(size, radius, radius_diff, True, ang=ang):
        #     pg.draw.rect(screen, (255, 0, 0), ((p.x + screen_size//4) * 2, (p.y + screen_size//4) * 2, 2, 2), 2)
        #     for dp in p.cns:
        #         pg.draw.line(screen, (0,255,0), ((p.x+ screen_size//4)*2,(p.y+ screen_size//4)*2), ((dp.x+ screen_size//4)*2, (dp.y+ screen_size//4)*2), 1)
        blocks, cds, hull = generate_tree(20)
        screen.fill((0, 0, 0))
        hull = shrink(hull, 2)
        # hull = shrink(hull, len(hull[0])-_idx)
        for b in blocks:
            pg.draw.rect(screen, b.color, (b.getX()-5, b.getY()-5, 10, 10))
        # for c in cds:
        #     pg.draw.circle(screen, (0,0,255), (int(c.x-3 + screen_size//4)*2,int(c.y-3+ screen_size//4)*2), 15, 2)
        for line in [l for subhull in hull for l in subhull]:
            c = (255, 0,0, 150) if (255,0,0, 150)==line[0].color==line[1].color else (0,255,0, 150)
            gfx.line(screen, int(line[0].getX()), int(line[0].getY()), int(line[1].getX()), int(line[1].getY()), c)

        pg.display.flip()
        time.sleep(2)

