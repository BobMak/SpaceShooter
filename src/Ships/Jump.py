import numpy as np
import pygame

from Core import Assets, State
from Core.Mechanics import Animation


class Jump(pygame.sprite.Sprite):
    """
    An object that teleports the source object to a certain direction and distance
    Attributes
    ----------
    source : GObject
        the object to teleport
    direction : float
        the direction to teleport the object to
    distance : float
        the distance to teleport the object to
    delay : float
        how long before the object gets teleportet
    """
    animation_id = 1425363
    def __init__(self, source, direction, distance, delay=10, state=None):
        """
        Parameters
        ----------
        source : GObject
            the object to teleport
        direction : float
            the direction to teleport the object to
        distance : float
            the distance to teleport the object to
        """
        super().__init__(state.time_dependent)
        if Jump.animation_id not in Animation.buffer:
            teleport_animation = Animation.generateExplosionAnimation(
                n_frames=delay,
                decay_rgb=(9, 6, 0),
                start_rgb=(255, 255, 255),

            )
            Animation.buffer[Jump.animation_id] = teleport_animation
        else:
            teleport_animation = Animation.buffer[Jump.animation_id]
        src_animation = Animation(
            teleport_animation[::-1],
            30,
            30,
            source.rect.x,
            source.rect.y,
            state=state
        )

        self.new_x = source.rect.x + distance * np.cos(np.deg2rad(direction-90))
        self.new_y = source.rect.y + distance * np.sin(np.deg2rad(direction-90))
        dst_animation = Animation(
            teleport_animation,
            30,
            30,
            self.new_x,
            self.new_y,
            state=state
        )
        self.source = source
        self.time_count = 0
        self.timer = delay
        source.locks[3] = True

    def update(self):
        if self.time_count == self.timer-1:
            self.source.pos = (self.new_x, self.new_y)