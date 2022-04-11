import time

import gym
import numpy as np
import pygame as pg

import Core.State as State
from Core.Scripts import step, spawn_wave, screen_draw
from Entities.Player import Player


class SpaceShooter(gym.Env):
    """
    Space Shooter environment
    """

    def __init__(self):
        """
        Initialize the environment
        action_space: [
            forward,
            backward,
            left,
            right,
            fire
        ]
        observation_space: a lidar scan of shape (16)
        concatenated with lidar linear velocities (16) and an angular velocity.
        The closer the object is to the agent, the higher the value
        """
        self.game_state = State.State()
        # Define the action space
        self.action_space = gym.spaces.Discrete(5)
        self.lidar_resolution = 16
        # Define the observation space
        self.observation_space = gym.spaces.Box(
            low=0.0, high=1.0, shape=(self.lidar_resolution*2 + 1,), dtype=np.float32
        )

        self.pg_initialized = False
        self.env_steps = 0

        self.reset()

    def reset(self):
        """
        Reset the environment
        """
        self.env_steps = 0
        # Reset the environment
        self.state = np.zeros(self.lidar_resolution*2 + 1)
        self.game_state.reset()
        Player.ship_assign(self.game_state.picked_ship, 1, self.game_state)
        self.game_state.pl.rect.center = (
            self.game_state.W // 2 + np.random.randint(-200, 200),
            self.game_state.H // 2 + np.random.randint(-200, 200))

        self.game_state.level = 3
        spawn_wave(self.game_state)

        # Return the initial observation
        return self.state

    def lidar_scan(self):
        # find asteroid distances
        for asteroid in self.game_state.asteroids:
            abs_angle = self.game_state.pl.get_aim_dir(asteroid)
            rel_angle = abs_angle - self.game_state.pl.look_dir
            lidar_i = int(rel_angle / 360 * 16)
            dist = self.game_state.pl.get_real_distance(asteroid)
            lidar_scan = 1 if dist < 1 else 1 / dist
            if self.state[lidar_i] < lidar_scan:
                self.state[lidar_i] = lidar_scan

        # find speed in each direction
        speed = np.sqrt(self.game_state.pl.v[0] ** 2 + self.game_state.pl.v[1] ** 2)
        abs_vel_angle = np.arctan2(self.game_state.pl.v[1], self.game_state.pl.v[0])
        rel_vel_angle = abs_vel_angle - self.game_state.pl.look_dir

        angle = -180
        angle_step = 360 / self.lidar_resolution
        for i in range(self.lidar_resolution, self.lidar_resolution*2):
            lidar_i_angle = int(self.lidar_resolution * (180 + rel_vel_angle) / 360)
            angle_diff = rel_vel_angle + angle
            self.state[lidar_i_angle] = speed * np.cos(angle_diff)
            angle += angle_step

    def step(self, action):
        """
        :param action:
        :return:
        """
        game_over = False
        reward = 0

        # Perform the action
        if action == 0:
            self.game_state.pl.accelerate(self.game_state.pl.acceleration)
        if action == 1:
            self.game_state.pl.accelerate(-self.game_state.pl.deacceleration)
        if action == 2:
            self.game_state.pl.rotate(-1)
        if action == 3:
            self.game_state.pl.rotate(1)
        if action == 4:
            self.game_state.pl.fire()

        # environment
        step(self.game_state)
        self.lidar_scan()
        self.state[-1] = self.game_state.pl.av  # angular velocity

        if self.game_state.pl.lives == 0:
            game_over = True
            reward += -1000

        # calculate reward based on distance to all asteroids and their size
        for asteroid in self.game_state.asteroids:
            dist = self.game_state.pl.get_distance(asteroid)
            r = 1 if dist < 1 else 1 / dist
            reward -= r * asteroid.type

        # reward for shooting asteroids
        for y in self.game_state.asteroids:
            for i in self.game_state.projectiles:
                if pg.sprite.collide_circle(y, i):
                    reward += 100

        # Return the observation, reward, and done flag
        self.game_state.clock.tick(self.game_state.LOGIC_PER_SECOND)

        return self.state, reward, game_over, {}

    def render(self, mode=None):
        """
        Render the environment
        """
        if mode == "human":
            if not self.pg_initialized:
                # Initialize the environment
                t_start = time.time()
                pg.init()

                print("re-init took:", time.time() - t_start)
                self.pg_initialized = True
            screen_draw(self.game_state)
            pg.display.flip()
            pg.display.update()

    def close(self):
        if self.pg_initialized:
            pg.quit()
            self.pg_initialized = False
        super().close()
