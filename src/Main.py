"""
Initial script
"""
import pygame
from src.Scripts import player_set
from src import State

pygame.init()
State.load_save()
# Load start menu
player_set()
