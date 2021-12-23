"""
using trained pytorch DRAW implementation by
https://github.com/Natsu6767/Generating-Devanagari-Using-DRAW
to generate ships
"""
import pygame.surfarray
import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import torchvision.utils as vutils
import time

from draw_model import DRAWModel


import numpy
import pygame.pixelcopy


def make_surface_rgba(array):
    """Returns a surface made from a [w, h, 4] numpy array with per-pixel alpha
    """
    shape = array.shape
    if len(shape) != 3 and shape[2] != 4:
        raise ValueError("Array not RGBA")

    # Create a surface the same width and height as array and with
    # per-pixel alpha.
    surface = pygame.Surface(shape[0:2], pygame.SRCALPHA, 32)

    # Copy the rgb part of array to the new surface.
    pygame.pixelcopy.array_to_surface(surface, array[:,:,0:3])

    # Copy the alpha part of array to the surface using a pixels-alpha
    # view of the surface.
    surface_alpha = numpy.array(surface.get_view('A'), copy=False)
    surface_alpha[:,:] = array[:,:,3]

    return surface


class Generator:
    def __init__(self, model_path='./data/models/model_final'):
        device = torch.device("cuda:0" if (torch.cuda.is_available()) else "cpu")
        state_dict = torch.load(model_path)
        params = state_dict['params']
        # Load the model
        self.model = DRAWModel(params).to(device)
        # Load the trained parameters.
        self.model.load_state_dict(state_dict['model'])

    def generateShipSurf(self, n=1):
        # Generate image sequence.
        with torch.no_grad():
            x = self.model.generate(n)

        z = x[-1].cpu().numpy().transpose(2, 1, 0)
        z = z * 255 / z.max()
        surf = make_surface_rgba(z.astype(np.uint8))
        # black close to black to alpha
        # surf.set_colorkey((0, 0, 0))
        # surf.set_colorkey((1, 1, 1))
        return surf