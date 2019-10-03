"""
Basic events and their mapping
"""
import pygame
import sys

import State

BASE = pygame.USEREVENT


def _quit():
    # graphics.alive = False
    sys.exit()


# Release all key locks
def _unpause():
    State.t = (True, True, True, True)
    pygame.time.set_timer(BASE + 1, 0)


def _stop_graphics():
    State.graphics.alive = False


# When approaching to a chunk bound
def _load_chunk():
    raise NotImplementedError()


# Event map
eve = {
    pygame.QUIT: _quit,
    BASE + 1: _unpause,
    BASE + 2: _stop_graphics,
}

