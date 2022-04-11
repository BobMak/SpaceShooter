from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

from matplotlib import pyplot as plt

import gym
import space_shooter_env


class MyCallback(BaseCallback):
    """
    Custom callback for saving a model every 100 steps
    """
    def __init__(self):
        super(MyCallback, self).__init__()
        self.rewards = []

    def _on_step(self):
        if self.n_calls % 1000 == 0:
            print("step", self.n_calls)


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
    )
    # model.collect_rollouts(env, )
    # model.train()

    model.learn(total_timesteps=1048576, callback=MyCallback())
    model.save("ppo_pilot")

    env.close()


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
        model.load("ppo_pilot")
    for x in range(5):
        done = False
        obs = env.reset()
        while not done:
            action, _states = model.predict(obs)
            obs, reward, done, info = env.step(action)
            env.render(mode="human")
    env.close()


if __name__ == '__main__':
    train_ppo()
    # evaulate(load=True)