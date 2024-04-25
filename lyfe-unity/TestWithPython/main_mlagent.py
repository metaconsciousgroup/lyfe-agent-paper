from pettingzoo import AECEnv
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.envs.unity_gym_env import UnityToGymWrapper
from mlagents_envs.envs.unity_aec_env import UnityAECEnv

from gym.spaces import Text, Dict, MultiDiscrete, Box
import random
import numpy as np
import os

FILENAME = "TestScene/mirror_mlagent_test.app"


def mlagent_test_main():
    unity_env = UnityEnvironment(file_name=FILENAME, seed=1, worker_id=1)
    env = UnityAECEnv(unity_env)

    for key, val in env._action_spaces.items():  # Look over all the agents
        # Add one extra dimension in the beginning to deal with MLAgent bug
        env._action_spaces[key] = Box(low=-2.0, high=2.0, shape=(1, 2), dtype=np.float32)

    env.reset()

    i = 0
    for agent in env.agent_iter(max_iter=100000):
        
        observations, reward, done, info = env.last()
        action = np.random.uniform(-2.0, 2.0, size=(1, 2))

        env.step(action)
        i += 1
    
    env.close()

if __name__ == "__main__":
    mlagent_test_main()