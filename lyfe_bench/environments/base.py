from typing import List

class BaseMultiAgentEnv:
    """Base class for multi-agent environments.
    
    This class is based on the PettingZoo API, but with some modifications.
    """
    def __init__(self, **kwargs):
        self._agent_ids: List[str] = []  # The list of agent ids
        pass

    @property
    def agent_ids(self):
        """Return the list of agent ids."""
        return self._agent_ids

    def observe(self, agent_id):
        """
        Observe should return the observation of the specified agent. This function
        should return a sane observation (though not necessarily the most up to date possible)
        at any time after reset() is called.
        """
        return None

    def reset(self, seed=None, options=None):
        """Reset the environment to its initial state.
        
        Args:
            seed (int): The random seed to use.
            options (Any): Any options to pass to the environment.
        """
        pass

    def step(self, agent_id, action):
        """Step through the environment with an agent's action.

        NOTE: This signature is different from Pettingzoo

        Args:
            agent_id (int): The agent's id.
            action (Any): The action to take.
        """
        pass

    def close(self):
        """
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        """
        pass