import numpy as np

def get_dist(dx, dy):
    return np.sqrt(dx**2 + dy**2)


def angle_diff(a1, a2):
    """angle_1 - angle_2 with regards to used angle system"""
    a = a1 - a2
    if abs(a) > 180:
        return np.sign(a)*360 - a
    else:
        return a
