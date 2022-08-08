import math

import numpy as np
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.callbacks import BaseCallback

import wandb
from matplotlib import pyplot as plt

import gym
import space_shooter_env


class WandbCallback(BaseCallback):
    def __init__(self):
        super(WandbCallback, self).__init__()
        self.steps = 0

    def _on_step(self):
        self.steps += 1
        if self.steps % 1000 == 0:
            print("step: ", self.steps)
            # wandb.log({"rewards": self.rewards})

def train_ppo():
    env = gym.make("SpaceShooter-v0")
    batch_size = 14000
    mini_batch_size = 3000
    n_epochs = 80
    model = PPO(
        "MlpPolicy",
        env, verbose=1,
        clip_range=0.02,
        n_steps=batch_size,
        n_epochs=n_epochs,
        batch_size=mini_batch_size,
        learning_rate=1e-3,
        policy_kwargs={"net_arch": [32, 32, 32, {'pi': [20], 'vf': [5]}]},
    )
    model.learn(total_timesteps=batch_size*n_epochs)  # total_timesteps=100000
    # model.learn(total_timesteps=1048576, callback=MyCallback())
    model.save("ppo_pilot")

    env.close()


def train_dqn():
    env = gym.make("SpaceShooter-v0")
    batch_size = 14000
    mini_batch_size = 3000
    n_epochs = 80
    model = DQN(
        "MlpPolicy",
        env, verbose=1,
        batch_size=mini_batch_size,
        learning_rate=1e-3,
        # policy_kwargs={"net_arch": [32, 32, 32, {'pi': [20], 'vf': [5]}]},
    )
    model.learn(total_timesteps=batch_size*n_epochs)  # total_timesteps=100000
    # model.learn(total_timesteps=1048576, callback=MyCallback())
    model.save("dqn_pilot")

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
            n_steps=config.batch_size,
            n_epochs=config.n_epochs,
            batch_size=max(1024, 1+config.batch_size // 4),
            learning_rate=1e-3,
            policy_kwargs={"net_arch": [*hidden_layers, actor_cirtic]},
        )
        model.learn(total_timesteps=config.n_epochs * config.batch_size, callback=WandbCallback())
        # model.learn(total_timesteps=1048576, callback=MyCallback())
        model.save("ppo_pilot")

        env.close()
def train_td3_wandb():
    with wandb.init(project="SpaceShooter", id="td3_pilot"):
        env = gym.make("SpaceShooter-v0")

        config = wandb.config
        hidden_layers = [config.hidden_size_common] * config.n_common_layers
        actor_cirtic = {
            'pi': [config.hidden_size_actor] * config.n_actor_layers,
            'vf': [config.hidden_size_critic] * config.n_critic_layers
        }
        env.setUseWandBParams(True, config.batch_size)
        model = TD3(
            "MlpPolicy",
            env, verbose=1,
            batch_size=max(1024, 1+config.batch_size // 4),
            learning_rate=1e-3,
            policy_kwargs={"net_arch": [*hidden_layers, actor_cirtic]},
        )
        model.learn(total_timesteps=config.n_epochs * config.batch_size, callback=WandbCallback())
        # model.learn(total_timesteps=1048576, callback=MyCallback())
        model.save("td3_pilot")

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
            'n_critic_layers': {'values': [1]},
            'hidden_size_common': {
                'distribution': 'q_log_uniform',
                'q': 1.0,
                'min': math.log(4),
                'max': math.log(128)
            },
            'hidden_size_actor': {'values': [10, 15, 20, 25]},
            'hidden_size_critic': {'values': [5, 10]},
            'clip_ratio': {'values': [0.02, 0.06, 0.1, 0.2, 0.3, 0.4]}
        }
    }
    sweep_id = wandb.sweep(sweep_config, project="SpaceShooter")
    wandb.agent(sweep_id, function=train_ppo_wandb, count=count)


def evaulate(load=False):
    env = gym.make("SpaceShooter-v0")
    print("evaluating...")
    actor_cirtic = {
        'pi': [10, 10],
        'vf': [10, 10]
    }
    n_epochs = 8
    batch_size = 8192
    model = PPO(
        "MlpPolicy",
        env, verbose=1,
        clip_range=0.2,
        n_steps=batch_size,
        batch_size=batch_size,
        n_epochs=n_epochs,
        policy_kwargs={"net_arch": [28, 20, actor_cirtic]},
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
    train_dqn()
    # sweep(100)