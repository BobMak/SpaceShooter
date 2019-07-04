"""
Initial script
"""
import pygame
from Scripts import player_set
import State

# TODO #1: Finish refactoring

# TODO: Modify event architecture. Scalability+ Add laziness
# TODO: Modify control mechanic
# TODO: Add abilities mechanic
# TODO: Add rpg-sim part
# TODO: Add Map. Store objects that exceed visibility
# TODO: Add Ship generation
# TODO: Space chunk transition behavior + big map + screen position update
# TODO: Separate all drawing from logic and place it in graphics thread.
# TODO: Modules that consist of several modules (e.g. maneuver thrusters, armor).
#  The integrity/efficiency of such modules may or may not be impacted by the loss of parts - maneuver thrusters
#  performance is reduced, while armor is only reduced locally
#       Keep a thread-safe list of draw calls in state that will be queried by graphics

pygame.init()

State.load_save()

player_set()
