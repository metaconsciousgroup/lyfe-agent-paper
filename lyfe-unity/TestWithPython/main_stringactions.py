from itertools import dropwhile
from pettingzoo import AECEnv
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.envs.unity_aec_env import UnityAECEnv

from gym.spaces import Text, Dict, MultiDiscrete, Box
import random
import numpy as np
import os

FILENAME = "TestScene/test_stringactions.app"


def remove_trailing_zeros(lst):
    return list(reversed(list(dropwhile(lambda x: x == 0, reversed(lst)))))


def ascii_to_string(observation):
    end_of_string_index = np.where(observation == 0.0)[0]

    # if string is empty or starts with 0
    # TODO: Robert's note, I think this line is a BUG, 
    # because if the observation is full (no 0 padding), then it will return None
    if end_of_string_index.size == 0:
        return None

    int_observations = observation[:end_of_string_index[0]].astype(np.uint8)
    string_observations = "".join([chr(i) for i in int_observations])  # Convert each UTF8 code back to string
    if string_observations == '':
        return None

    return string_observations


def string_to_ascii(text, max_len=100):
    # Convert each character to UTF8 code
    # if there is no enough space, truncate the text
    # if there is space left, fill with 0
    if text == "[NONE]":
        return [0] * max_len
    elif len(text) < max_len:
        return [ord(char) for char in text] + [0] * (max_len - len(text))
    else:
        return [ord(char) for char in text[:max_len]]


def mlagent_test_main():
    unity_env = UnityEnvironment(file_name=FILENAME, seed=1, worker_id=1)
    env = UnityAECEnv(unity_env)

    # NOTE: This funny shape is a workaround for Unity-pettingzoo bug
    # NOTE: change the action space whenever the action space in Unity Editor changes
    for key, val in env._action_spaces.items():
            env._action_spaces[key] = MultiDiscrete(np.array([[128] * 200]))

    env.reset()

    i = 0
    for agent in env.agent_iter(max_iter=5):
        print(agent)

        ## TODO: What's the action_mask thing, and is our main code generating it?
        observations, reward, done, info = env.last()
        observations = observations["observation"]
        # print(observations)
        print('')
        print("Observation")
        print(ascii_to_string(observations[0]))
        print("Action")
        action1 = "I'm first: " + str(np.random.randint(0, 100))
        action2 = "I'm second: " + str(np.random.randint(0, 100))
        action3 = "I'm third: " + str(np.random.randint(0, 100))
        print(action1 + action2 + action3)
        action1 = string_to_ascii(action1, max_len=50)
        action2 = string_to_ascii(action2, max_len=50)
        action3 = string_to_ascii(action3, max_len=100)
        action = action1 + action2 + action3

        env.step([action])
        i += 1
    
    env.close()


if __name__ == "__main__":
    mlagent_test_main()