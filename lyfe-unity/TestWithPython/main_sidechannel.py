from pettingzoo import AECEnv
from mlagents_envs.environment import UnityEnvironment
from mlagents_envs.envs.unity_gym_env import UnityToGymWrapper
from mlagents_envs.envs.unity_aec_env import UnityAECEnv

from gym.spaces import Text, Dict, MultiDiscrete, Box
import random
import numpy as np
import os

try:
    from environments.unity import OutgoingMessage, TextSideChannel
except ImportError:
    print("This needs to be fixed!!")

from mlagents_envs.side_channel import SideChannel, IncomingMessage, OutgoingMessage
import uuid

def name_lower2higher(name):
    return ' '.join(name.split('_')).title()


FILENAME = "TestScene/sidechannel.app"


def sidechannel_test_main():
    text_channel = TextSideChannel()
    unity_env = UnityEnvironment(file_name=FILENAME, seed=1, side_channels=[text_channel], worker_id=1)

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

        if i % 100 == 0:
            # Send a message to Unity
            text_channel.send_message(f"host|client|Counter: {i}")
            print(f"[Python][When send] host|client|Counter: {i}")
    
    env.close()


if __name__ == "__main__":
    sidechannel_test_main()