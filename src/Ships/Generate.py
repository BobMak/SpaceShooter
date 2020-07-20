import numpy as np
import random as r
import copy

from Core import Utils

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
        angle = r.random() * 2 * np.pi
        x = np.cos(angle) * radius + r.uniform(-radius_var, radius_var)
        y = np.sin(angle) * radius + r.uniform(-radius_var, radius_var)
        points.append((x,y))
        if symmetry:
            points.append((-x, y))
    return points


def generate_skeleton_triangle(size, radius, radius_var, symmetry=True, ang=1.0):
    points = []
    size = size//2 if symmetry else size
    for point in range(size):
        x = r.uniform(-radius, radius) + r.uniform(-radius_var, radius_var)
        y = radius - (ang * np.absolute(x)) + r.uniform(-radius_var, radius_var)
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
    x, y = 0, 0
    ang = 0
    points.append(Point(x,y))
    if symmetry:
        size=size//2  # will copy left side points to the right
    for point in range(size):
        # start growing from different point
        if r.random() < branching:
            newPivot = r.choice(points)
            x, y = newPivot.x, newPivot.y
        attempts=0
        # Try to generate a new point that is n pixels away from any other point.
        while True:
            _dist = r.normalvariate(dist, ddist)  # a random distance to a new point
            ang += r.uniform(-dang, dang)         # new angle shouldn't change too fast
            x += _dist * np.cos(np.deg2rad(ang))
            y += _dist * np.sin(np.deg2rad(ang))
            p = Point(x, y)
            if p.getClosest(points)[0].getDist(p) > 10:
                break
            elif attempts > 10:
                newPivot = r.choice(points)
                x, y = newPivot.x, newPivot.y
                attempts = 0
            attempts+=1
        points.append(p)
        if symmetry:
            points.append(Point(-x, y))
    # do k-means to create centers and connect all module centers
    cds = {}

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
            p2 = r.choice(_hull_points)
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
        # TODO: don't cut the line if it leaves a hanging point.
        # TODO: cut shorter lines first.
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

