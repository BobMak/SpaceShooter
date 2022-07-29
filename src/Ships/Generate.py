import math

import numpy as np
import random as r
import copy

import pygame as pg
import pygame.transform as tr
import pygame.image as img
import pygame.gfxdraw as gfx

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

    def getClosest(self, points, allow_self=False):
        if not allow_self:
            if self in points:
                points.remove(self)
        points.sort(key=lambda a: self.getDist(a))
        return points

    def __getitem__(self, item):
        if item==0:
            return self.x
        elif item==1:
            return self.y
        else:
            raise IndexError("Index out of range")


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


def make_hull(points):
    _hull_points = copy.deepcopy(points)
    # Add hull
    hull = []
    _hull_points.sort(key=lambda p: p.x)
    p1 = _hull_points[0]
    while True:
        p2 = r.choice(_hull_points)
        for p in _hull_points:
            if Utils.orientation(p1, p2, p) == 1:
                p2 = p
        if (p1, p2) in hull or (p2, p1) in hull:  # Exit condition - lines form a cycle
            break
        hull.append((p1, p2))
        p1 = p2
    for pair in hull:  # remove points from
        try:
            _hull_points.remove(pair[0])
        except:
            pass
        try:
            _hull_points.remove(pair[1])
        except:
            pass
    return hull, _hull_points


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
    while len(_hull_points)>=3:  # add new layers while there are points
        subHull, _hull_points = make_hull(_hull_points)
        hull.append(subHull)
    return points, cds, hull


def shrink(hull: [[(Point, Point)]], n_points, symmetry=False):
    """given a hull with n layers and a parameter A, replace connections in
    outer layers with connections to inner layers.
    Replace a line in the outer layer with two lines going to an inner layer
    :param hull: set of layers"""
    outer = hull[0]
    inner = [l for subhull in hull[1:] for l in subhull]  # get lines from list of lists of lines
    for idx in range(n_points):
        try:
            idx=idx*2
            _outer_points = [p for l in outer for p in l]
            _inner_points = [p for l in inner for p in l]
            if idx >= len(outer):
                break
            p1, p2 = outer[idx]  # outer edge to be removed

            # find closest line from the inner edge
            new_p1 = p1.getClosest(_inner_points)[0]
            _inner_points.remove(new_p1)
            new_p2 = p2.getClosest(_inner_points)[0]
            p1.color, new_p1.color = (255, 0, 0, 150), (255, 0, 0, 150)
            p2.color, new_p2.color = (255, 0, 0, 150), (255, 0, 0, 150)
            outer[idx] = (p1, new_p1)
            outer.insert(idx+1, (p2, new_p2))
            # outer.extend([, (p2, new_p2)])
            # del outer[idx]
            if symmetry:
                # corresponding line on the other side
                inv_p1 = Point(-p1.x, p1.y).getClosest(_outer_points, allow_self=True)[0]  # [x for line in outer for x in line]
                _outer_points.remove(inv_p1)
                inv_p2 = Point(-p2.x, p2.y).getClosest(_outer_points, allow_self=True)[0]  # get the inverse side of that
                # if (inv_p2, inv_p1) in outer:
                #     inv_idx = outer.index((inv_p2, inv_p1))
                # elif (inv_p1, inv_p2) in outer:
                #     inv_idx = outer.index((inv_p1, inv_p2))
                # else:
                #     print('no inverse point')
                #     continue
                inv_idx = -idx-1
                # a new opposite side line in the inner layer
                new_inv_p1 = Point(-new_p1.x, new_p1.y).getClosest(_inner_points)[0]
                _inner_points.remove(new_inv_p1)
                new_inv_p2 = Point(-new_p2.x, new_p2.y).getClosest(_inner_points)[0]
                # del outer[inv_idx]
                outer[inv_idx] = (inv_p1, new_inv_p1)
                outer.insert(inv_idx, (inv_p2, new_inv_p2))
                inv_p1.color, new_inv_p2.color = (255, 0, 0, 150), (255, 0, 0, 150)
                inv_p2.color, new_inv_p2.color = (255, 0, 0, 150), (255, 0, 0, 150)
                # outer.extend([(inv_p1, new_inv_p1), (inv_p2, new_inv_p2)])
        except:
            pass
    return hull


def normal_points(center_point, n=5, std=5.0):
    return [Point(r.normalvariate(center_point[0], std), r.normalvariate(center_point[1], std)) for _ in range(n)]


def generate_normals(center, npoints=5, std=5.0, nrecurs=1, dstd=1.0, leafhull=False, symmetric=False):
    """
    generates a few point clusters with random points scattered around those
    :param nclusers:
    :param npoints:
    :param std:
    :return:
    """
    all_points = []
    points = normal_points(center, npoints, std)
    if symmetric:
        points = add_symmetry(points)
    hull = []
    if nrecurs > 0:
        for p in points:
            p.color = (255, 0, 0, 150)
            _points, _hull = generate_normals(p, npoints, std-dstd, nrecurs-1, leafhull=leafhull, symmetric=symmetric)
            all_points.extend(_points)
            if leafhull:
                hull.extend(_hull)
    all_points.extend(points)
    _hull_points = copy.deepcopy(all_points)
    # Add hull
    _layer = 0
    if leafhull:
        subHull, _hull_points = make_hull(_hull_points)
        if len(subHull) > 2:
            hull.append(subHull)
        hull = hull[::-1]
    else:
        while len(_hull_points) >= 3:  # add new layers while there are points
            subHull, _hull_points = make_hull(_hull_points)
            if len(subHull)>2:
                hull.append(subHull)
    return all_points, hull


def generate_poly(size,
                  temperature=0.5,
                  sharpness=0.0,
                  cuttosize=True):
    surface = pg.Surface(size)
    n_points = max(3, int((1.0-sharpness)*10))
    n_recurs = max(1, int(min(n_points**2, temperature*3)))
    n_verticies_to_remove = int(sharpness*(n_points-1))
    leafhull = True if sharpness > 0.5 else False

    green_blue_tmp = temperature**2 / math.exp(1)
    clr = (int(temperature*255), int(green_blue_tmp*255), min(255,int((1.0-temperature)*255)), 100+int(temperature*100))

    blocks, hull = generate_normals(
        center=(0, 0),  # (screen.get_width()//2, screen.get_height()//2)
        npoints=n_points,
        nrecurs=n_recurs,
        std=size[0]/10,
        dstd=size[0]/20,
        leafhull=leafhull,
    )
    surface.fill((0, 0, 0))
    hull = shrink(hull, n_verticies_to_remove)
    pg.event.pump()
    # make sure all points fit inside the surface
    # maxx = int(max([p.getX() for p in blocks]))
    # maxy = int(max([p.getY() for p in blocks]))
    #
    # x_error_bias = maxx - size[0]
    # y_error_bias = maxy - size[1]
    # for p in blocks:
    #     p.x -= x_error_bias
    #     p.y -= y_error_bias
    # minx = int(min([p.getX() for p in blocks]))
    # miny = int(min([p.getY() for p in blocks]))
    # scale_error = max(abs(minx/size[0]), abs(miny/size[1]))
    # for p in blocks:
    #     p.x /= scale_error
    #     p.y /= scale_error

    for subhull in hull:
        gfx.filled_polygon(surface, [(p.getX(), p.getY()) for l in subhull for p in l], clr)

    # if cuttosize:
    #     surface = surface.subsurface(pg.Rect(minx, miny, maxx, maxy))
    pg.display.flip()
    return surface, blocks, hull


def add_symmetry(points):
    """
    add symmetry to a set of points
    :param points:
    :return:
    """
    return points + [Point(-x, y) for x, y in points]


def save_img(surface, filename, size=(100,100)):
    surf = tr.scale(surface, size)
    img.save(surf, filename)