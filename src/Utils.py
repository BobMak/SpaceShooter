import numpy as np


def get_dist(dx, dy):
    return np.sqrt(dx**2 + dy**2)


def angle_diff(a1, a2):
    """difference in degrees"""
    if a1 < 0:
        a1 += 360
    if a2 < 0:
        a2 += 360
    assert 0 <= a1 < 361, "a1 outs of bounds: {}".format(a1)
    assert 0 <= a2 < 361, "a2 outs of bounds: {}".format(a2)
    a = a2 - a1
    if abs(a) > 180:
        a= a - np.sign(a)*360
    assert -180<=a<=180, "angle outs of bounds: {}".format(a)
    return a


def orientation(a, b, c):
    """Jarviss algorithm for convex graph wrapping"""
    val = (a.y - c.y) * (b.x - a.x) - (a.x - c.x) * (b.y - a.y)
    if val == 0:
        return 0
    else:
        return 1 if val > 0 else 2