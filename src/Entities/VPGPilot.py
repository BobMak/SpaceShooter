import math

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

import wandb
from matplotlib import pyplot as plt

import gym
import space_shooter_env


class WandbCallback(BaseCallback):
    def __init__(self):
        super(WandbCallback, self).__init__()
        self.rewards = 0
        self.steps = 0

    def _on_step(self):
        self.steps += 1
        if self.steps % 1000 == 0:
            print("step: ", self.steps)
            # wandb.log({"rewards": self.rewards})
            self.rewards = 0

def train_ppo():
    env = gym.make("SpaceShooter-v0")
    model = PPO(
        "MlpPolicy",
        env, verbose=1,
        clip_range=0.2,
        n_steps=8192,
        n_epochs=20,
        batch_size=512,
        learning_rate=1e-3,
        policy_kwargs={"net_arch": [16, 10, {'pi': [5], 'vf': [16]}]},
    )
    model.learn(total_timesteps=100000)
    # model.learn(total_timesteps=1048576, callback=MyCallback())
    model.save("ppo_pilot")

    env.close()


def train_ppo_wandb():
    with wandb.init(project="SpaceShooter"):
        env = gym.make("SpaceShooter-v0")

        config = wandb.config
        hidden_layers = [config.hidden_size_common] * config.n_common_layers
        actor_cirtic = {
            'pi': [config.hidden_size_actor] * config.n_actor_layers,
            'vf': [config.hidden_size_critic] * config.n_critic_layers
        }
        env.setUseWandBParams(True, config.batch_size)
        model = PPO(
            "MlpPolicy",
            env, verbose=1,
            clip_range=config.clip_ratio,
            n_steps=config.n_epochs * config.batch_size,
            n_epochs=config.n_epochs,
            batch_size=config.batch_size,
            learning_rate=1e-3,
            policy_kwargs={"net_arch": [*hidden_layers, actor_cirtic]},
        )
        model.learn(total_timesteps=config.n_epochs * config.batch_size, callback=WandbCallback())
        wandb.log({"rewards": 0.0})
        # model.learn(total_timesteps=1048576, callback=MyCallback())
        model.save("ppo_pilot")

        env.close()

def sweep(count=10):
    sweep_config = {
        'method': 'random',
        'metric': {
            'name': 'rewards',
            'goal': 'maximize'
        },
        'parameters': {
            'batch_size': {
                'distribution': 'q_log_uniform',
                'q': 1.0,
                'min': math.log(800),
                'max': math.log(20000)
            },
            'n_epochs': {'values': [30, 40, 50, 80]},
            'n_common_layers': {'values': [1, 2, 3]},
            'n_actor_layers': {'values': [1, 2, 3]},
            'n_critic_layers': {'values': [1, 2, 3]},
            'hidden_size_common': {
                'distribution': 'q_log_uniform',
                'q': 1.0,
                'min': math.log(4),
                'max': math.log(128)
            },
            'hidden_size_actor': {'values': [5, 10, 15]},
            'hidden_size_critic': {'values': [5, 10, 15]},
            'clip_ratio': {'values': [0.02, 0.06, 0.1, 0.2, 0.3, 0.4]}
        }
    }
    sweep_id = wandb.sweep(sweep_config, project="SpaceShooter")
    wandb.agent(sweep_id, function=train_ppo_wandb, count=count)


def evaulate(load=False):
    env = gym.make("SpaceShooter-v0")
    print("evaluating...")
    model = PPO(
        "MlpPolicy",
        env, verbose=1,
        clip_range=0.2,
        n_steps=8192,
        n_epochs=5,
        batch_size=512,
    )
    if load:
        model = PPO.load("ppo_pilot")
    for x in range(5):
        done = False
        obs = env.reset()
        rewards = []
        while not done:
            action, _states = model.predict(obs)
            obs, reward, done, info = env.step(action)
            rewards.append(reward)
            env.render(mode="human")
        print("episode reward:", sum(rewards))
    env.close()


if __name__ == '__main__':
    # train_ppo()
    # evaulate(load=True)
    sweep(100)