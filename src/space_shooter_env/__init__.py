from gym.envs.registration import (
    registry,
    register,
    make,
    spec,
    load_env_plugins as _load_env_plugins,
)

# Hook to load plugins from entry points
_load_env_plugins()

register(
    id="SpaceShooter-v0",
    entry_point="space_shooter_env.envs:SpaceShooter",
    max_episode_steps=1000,
    # reward_threshold=1.0,
)

register(
    id="SpaceShooterNav-v0",
    entry_point="space_shooter_env.envs:SpaceShooterNav",
    max_episode_steps=1000,
    reward_threshold=1.0,
)
