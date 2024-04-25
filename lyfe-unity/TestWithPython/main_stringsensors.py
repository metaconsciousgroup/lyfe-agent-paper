from itertools import dropwhile
from pettingzoo import AECEnv
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.envs.unity_gym_env import UnityToGymWrapper
from mlagents_envs.envs.unity_aec_env import UnityAECEnv

from gym.spaces import Text, Dict, MultiDiscrete, Box
import random
import numpy as np
import os

FILENAME = "TestScene/test_stringsensors.app"


def remove_trailing_zeros(lst):
    return list(reversed(list(dropwhile(lambda x: x == 0, reversed(lst)))))


def print_string_observation(observation):
    observation = observation.astype(np.uint8)
    observation = remove_trailing_zeros(observation)
    
    if not observation:
        return None

    # int_observations = observation.astype(np.uint8)
    string_observations = "".join([chr(i) for i in observation])  # Convert each UTF8 code back to string
    print(string_observations)


def mlagent_test_main():
    unity_env = UnityEnvironment(file_name=FILENAME, seed=1, worker_id=1)
    env = UnityAECEnv(unity_env)

    for key, val in env._action_spaces.items():  # Look over all the agents
        # Add one extra dimension in the beginning to deal with MLAgent bug
        env._action_spaces[key] = Box(low=-2.0, high=2.0, shape=(1, 2), dtype=np.float32)

    env.reset()

    i = 0
    for agent in env.agent_iter(max_iter=10):
        print(agent)
        
        observations, reward, done, info = env.last()

        for i, observation in enumerate(observations):
            print(i)
            print(observation.shape)
            if i in [3, 4, 5]:
                print(observation)
                print_string_observation(observation)

        action = np.random.uniform(-2.0, 2.0, size=(1, 2))
        
        # print_string_observation(observations[0])

        env.step(action)
        i += 1
    
    env.close()


if __name__ == "__main__":
    mlagent_test_main()