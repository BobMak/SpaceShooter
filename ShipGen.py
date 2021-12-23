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


class Generator:
    def __init__(self, model_path='./data/models/model_a16_64'):
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
        surf = pygame.surfarray.make_surface(z)
        # black close to black to alpha
        surf.set_colorkey((0, 0, 0))
        # surf.set_colorkey((1, 1, 1))

        return surf