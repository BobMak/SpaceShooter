import numpy as np
import cupy as cp
import random
from numba import njit, cuda
import matplotlib.pyplot as plt


filter = np.array([
    [1, 1, 1],
    [1, 0, 1],
    [1, 1, 1],
], dtype=np.uint64)


@cuda.jit
def increment_a_2D_array(an_array, filter):
    x, y = cuda.grid(2)
    if x < an_array.shape[0] and y < an_array.shape[1]:
        # can't use * since an_array's layout is A(any) and filter's layout is C(contiguous)
        # can't use & for the same reason
        # can't use np.multiply since its not supported
        s = (an_array[x-1:x+2, y-1:y+2] * filter).sum()
        if s > 3 and s < 6:
            an_array[x, y] = 1
        else:
            an_array[x, y] = 0


randimg = cp.random.randint(0, 2, size=(100, 100), dtype=np.uint64)
kernel = cp.ElementwiseKernel(
    'raw T x',
    'T y',
    '; '
    'y = x',
)
imgs = [randimg]

threadsperblock = (10, 10)
blockspergrid = (int(randimg.shape[0] / threadsperblock[0]), int(randimg.shape[1] / threadsperblock[1]))

plt.ion()
for i in range(100):
    # randimg = increment_a_2D_array[blockspergrid, threadsperblock](randimg, filter)
    imgs.append(randimg)

for i in range(100):
    plt.imshow(imgs[i], cmap='gray')

plt.show()