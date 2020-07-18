"""
Initial script
"""
import pygame
from Core import State

pygame.init()
# Load start menu
State.init()
from Core.Scripts import main_loop


main_loop()
