import logging
import copy
from typing import List, Optional

from lyfe_python_env.datatype import UnityAgent
from lyfe_python_env.datatype.unity_player import UnityPlayer

logger = logging.getLogger(__name__)


class UnityAgentPlayerManager:
    def __init__(self):
        """This class contains information about the agents and players in the game.

        Note: This class is not thread safe. Should consider separating player and agent entities.
        """
        self.__player_dict: dict[str, UnityPlayer] = {}
        self.__agent_dict: dict[str, UnityAgent] = {}
        # TODO: A dictionary of usernames to ids is not safe because usernames are not unique
        self.__username_to_id_dict: dict[str, str] = {}

    def username_to_id(self, username: str) -> Optional[str]:
        return self.__username_to_id_dict.get(username, None)

    @property
    def agent_usernames(self) -> List[str]:
        return [agent.user.username for agent in self.__agent_dict.values()]

    def get_agent_list(self) -> List[UnityAgent]:
        return list(self.__agent_dict.values())

    def get_agent_id_list(self) -> List[str]:
        return list(self.__agent_dict.keys())

    @property
    def player_usernames(self) -> List[str]:
        return [player.user.username for player in self.__player_dict.values()]

    def get_player_list(self) -> List[UnityPlayer]:
        return list(self.__player_dict.values())

    def get_player_id_list(self) -> List[str]:
        return list(self.__player_dict.keys())

    def add_agent(self, agent: UnityAgent) -> bool:
        key: str = agent.user.id

        # Invalid string key
        if not key:
            KeyError(
                "{0}.{1} invalid agent id null or empty".format(
                    UnityAgentPlayerManager.__name__, self.__name__
                )
            )
            return False

        # Tried adding agent with duplicate id
        if key in self.__agent_dict:
            KeyError(
                "{0}.{1} duplicate agent id '{2}' already exists".format(
                    UnityAgentPlayerManager.__name__, self.__name__, key
                )
            )
            return False

        self.__agent_dict[key] = agent
        self.__username_to_id_dict[agent.user.username] = key
        return True

    def add_agents(self, agents: List[UnityAgent]) -> None:
        for agent in agents:
            self.add_agent(agent)

    def get_agent(self, agent_id: str) -> Optional[UnityAgent]:
        if not agent_id:
            return None

        if agent_id not in self.__agent_dict:
            # KeyError("agent id '{0}' does not exist".format(agent_id))
            return None

        return self.__agent_dict[agent_id]

    def get_agents(self, agent_id_list: List[str]) -> List[UnityAgent]:
        if not agent_id_list:
            return []
        agents: List[UnityAgent] = []
        for i in agent_id_list:
            unity_agent: Optional[UnityAgent] = self.get_agent(i)
            if unity_agent is not None:
                agents.append(unity_agent)
            else:
                logger.warning(
                    "Failed to find agent with id '{0}' in unity scene".format(i)
                )
        return agents

    @property
    def player_dict(self):
        return copy.copy(self.__player_dict)

    def get_player(self, player_id: str) -> Optional[UnityPlayer]:
        if not player_id:
            # KeyError("Invalid agent id null or empty")
            return None

        if player_id not in self.__player_dict:
            # KeyError("player id '{0}' does not exist".format(player_id))
            return None

        return self.__player_dict[player_id]

    def get_players(self, player_id_list: List[str]) -> List[UnityPlayer]:
        if not player_id_list:
            return []
        players: List[UnityPlayer] = []
        for i in player_id_list:
            unity_player: Optional[UnityPlayer] = self.get_player(i)
            if unity_player is not None:
                players.append(unity_player)
            else:
                logger.warning("Failed to find player with id '{0}' in unity".format(i))
        return players

    def add_player(self, player: UnityPlayer) -> bool:
        key: str = player.user.id

        # Invalid string key
        if not key:
            KeyError("Invalid player id null or empty")
            return False

        # Tried adding agent with duplicate id
        if key in self.__player_dict:
            KeyError("duplicate player id '{0}' already exists".format(key))
            return False

        self.__player_dict[key] = player
        self.__username_to_id_dict[player.user.username] = key
        return True

    def update_player(self, player: UnityPlayer) -> bool:
        key: str = player.user.id

        # Invalid string key
        if not key:
            KeyError("Invalid player id null or empty")
            return False
        elif key not in self.__player_dict:
            KeyError("Player id '{0}' does not exist".format(key))
            return False

        self.__player_dict[key] = player
        self.__username_to_id_dict[player.user.username] = key
        return True

    def remove_player(self, player_id: str) -> bool:
        # Invalid string key
        if not player_id:
            KeyError("Remove player failed: Invalid player id null or empty")
            return False

        # Tried adding agent with duplicate id
        if player_id not in self.__player_dict:
            KeyError(
                "Remove player failed: Player id '{0}' does not exist".format(player_id)
            )
            return True

        self.__player_dict.pop(player_id)
        return True
