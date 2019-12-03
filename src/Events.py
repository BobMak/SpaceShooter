"""
Basic events and their mapping
"""
import pygame
import sys
import random as r

import State
# Index event - BASE to get the desired event from eve list
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


def post_event(_fun, args, timer, id=None):
    # Event with custom id. In case you need to know id in advance
    if id and id not in eve:
        eve[id] = (_fun, args)
        pygame.time.set_timer(id, timer)
        return id
    elif id:
        return 0
    elif not id:
        while True:  # Generate unique event id
            rand_id = r.randint()
            if rand_id not in eve:
                eve[rand_id] = (_fun, args)
                pygame.time.set_timer(rand_id, timer)
                return rand_id


# Event map. Callbacks with their args. eve[123][0](*eve[123][1])
eve = {
    pygame.QUIT:     (_quit, ()),
    BASE+1:       (_unpause, ()),
    BASE+2: (_stop_graphics, ()),
}
