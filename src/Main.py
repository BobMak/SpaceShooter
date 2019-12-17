"""
Initial script
"""
import pygame
import State
pygame.init()
# Load start menu
State.init()
from Scripts import main_loop
main_loop()
