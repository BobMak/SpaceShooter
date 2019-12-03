"""
Initial script
"""
import pygame
from Scripts import player_set
import State

pygame.init()
State.load_save()
# Load start menu
player_set()
