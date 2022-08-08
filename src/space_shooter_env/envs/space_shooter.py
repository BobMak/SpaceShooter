import copy

import gym
import numpy as np
import pygame as pg
import wandb

import Core.State as State
from Core.Mechanics import GObject
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
            low=0.0, high=1.0, shape=(self.lidar_resolution*2 + 5,), dtype=np.float32
        )

        self.prev_lidar_scan = np.zeros(self.lidar_resolution)

        self.pg_initialized = False
        self.env_steps = 0

        self.reset()
        self.usewandb = False
        self.ep_lengths = []
        self.last_ep_i = 0
        self.rollout_reward = 0
        self.rollout_count = 0
        self.rollout_length = 1000

    def setUseWandBParams(self, usewandb, rollout_length):
        self.usewandb = usewandb
        self.rollout_length = rollout_length

    def reset(self):
        """
        Reset the environment
        """
        wave_config = {
            'hps': 5,
            'velocity_deviations': 1.0,
            'noclip_timers': 10,
            'densities': (2,3),
            'number': 10,
            'init_speed': 5.0,
            'img_n': 3
        }

        self.env_steps = 0
        # Reset the environment
        self.state = np.zeros(sum(self.observation_space.shape))
        self.game_state.reset()
        Player.ship_assign(self.game_state.picked_ship, 1, self.game_state)
        self.game_state.pl.rect.center = (
            self.game_state.W // 2 + np.random.randint(-200, 200),
            self.game_state.H // 2 + np.random.randint(-200, 200)
        )

        spawn_wave(self.game_state, wave_config=wave_config)

        self.rollout_reward = 0
        # Return the initial observation
        return self.state

    def lidar_scan(self):
        lidar_scan = np.zeros(self.lidar_resolution)
        # find asteroid distances
        for asteroid in self.game_state.asteroids:
            dist, angle = self.game_state.pl.get_real_distance(asteroid)
            # rel_angle = abs_angle - self.game_state.pl.look_dir
            lidar_i = int((self.lidar_resolution-1)*angle / 360)
            lidar_d = 1 if dist < 1 else 1 / dist
            if lidar_scan[lidar_i] < lidar_d:
                lidar_scan[lidar_i] = lidar_d
        # set state to differences between current and previous lidar scan
        self.state[:self.lidar_resolution] = lidar_scan
        self.state[self.lidar_resolution:2*self.lidar_resolution] = lidar_scan - self.prev_lidar_scan
        self.prev_lidar_scan = lidar_scan

    def step(self, action):
        """
        :param action:
        :return:
        """
        game_over = False
        reward = 0.1

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

        # get the new observation
        self.state = np.zeros(sum(self.observation_space.shape))
        self.lidar_scan()
        # angular velocity
        self.state[-1] = self.game_state.pl.av
        # egocentric velocity
        vel1 = self.game_state.pl.v[0] * np.cos(np.deg2rad(self.game_state.pl.look_dir-90))

        if np.sign(vel1) > 0:
            self.state[-2] = vel1
        else:
            self.state[-3] = vel1
        vel2 = self.game_state.pl.v[1] * np.sin(np.deg2rad(self.game_state.pl.look_dir-90))
        if np.sign(vel2) > 0:
            self.state[-4] = vel2
        else:
            self.state[-5] = vel2

        if self.game_state.pl.lives == 0:
            game_over = True
            reward += -1000

        # calculate reward based on distance to all asteroids and their size
        # for asteroid in self.game_state.asteroids:
        #     dist = self.game_state.pl.get_distance(asteroid)
        #     r = 1 if dist < 1 else 1 / dist
        #     reward -= r * asteroid.type

        # reward for shooting asteroids
        for y in self.game_state.asteroids:
            for i in self.game_state.projectiles:
                if pg.sprite.collide_circle(y, i):
                    reward += 100

        # reward moving faster
        speed = np.sqrt(self.game_state.pl.v[0]**2 + self.game_state.pl.v[1]**2)
        reward += speed * 0.1

        # Return the observation, reward, and done flag
        self.game_state.clock.tick(self.game_state.LOGIC_PER_SECOND)

        if self.usewandb:
            self.rollout_reward += reward
            self.rollout_count+= 1
            if self.rollout_count > self.rollout_length and game_over:
                wandb.log({
                    "rewards": self.rollout_reward/self.rollout_count,
                    "avg_length": sum(self.ep_lengths)/len(self.ep_lengths)
                })
                self.rollout_count = 0
                self.rollout_reward = 0
                self.ep_lengths = []
                self.last_ep_i = 0
            elif game_over:
                self.ep_lengths.append(self.rollout_count - self.last_ep_i)
                self.last_ep_i = self.rollout_count

        return self.state, reward, game_over, {}

    def render(self, mode=None):
        """
        Render the environment
        """
        if mode == "human":
            if not self.pg_initialized:
                # Initialize the environment
                pg.init()
                self.pg_initialized = True
            screen_draw(self.game_state)

            # draw the lidar lines from the player
            for i in range(self.lidar_resolution):
                lidar_dist = 1000
                angle = self.game_state.pl.look_dir + i * 360 / self.lidar_resolution - 90
                x = self.game_state.pl.rect.center[0] + lidar_dist * np.cos(np.deg2rad(angle))
                y = self.game_state.pl.rect.center[1] + lidar_dist * np.sin(np.deg2rad(angle))
                # lines with greater value are brighter
                clr = (np.clip(255 * self.state[i]*65535, a_min=0, a_max=255).item(),
                       np.clip(255 * self.state[i]*255, a_min=0, a_max=255).item(),
                       np.clip(255 * self.state[i], a_min=0, a_max=255).item())
                pg.draw.line(self.game_state.screen, clr, self.game_state.pl.rect.center, (x, y), 1)

            pg.display.flip()
            pg.display.update()

    def close(self):
        if self.pg_initialized:
            pg.quit()
            self.pg_initialized = False
        super().close()
