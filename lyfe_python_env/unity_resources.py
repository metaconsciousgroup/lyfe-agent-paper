import logging
from typing import List
import uuid

from lyfe_python_env.datatype import (
    UnityTransform,
    UnityUser,
    UnityAgent,
    UnityCharacter,
)
from lyfe_python_env.datatype.send_out import OutDataAgent, OutDataScene
from lyfe_python_env.datatype.unity_player import UnityPlayer
from lyfe_python_env.unity_agent_player_manager import UnityAgentPlayerManager


logger = logging.getLogger(__name__)


class UnityResources:

    def __init__(self):
        self._unity_agent_player_manager: UnityAgentPlayerManager = (
            UnityAgentPlayerManager()
        )

    def __create_user(self, username: str) -> UnityUser:
        return UnityUser(
            id=f"UnityUser-{uuid.uuid4()}",
            username=username,
        )

    def __create_agent(
        self, user: UnityUser, character: UnityCharacter, transform: UnityTransform
    ) -> UnityAgent:
        return UnityAgent(user=user, character=character, transform=transform)

    def create_scene_from_dict(self, data: dict) -> OutDataScene:
        if data["messageType"] != "GAME_DATA":
            raise Exception("Invalid message type")
        lobby = data.get("lobby", {})
        location = lobby.get("location", {})
        title = location.get("name", None)

        # Your existing conditionals
        if title == "City (Day)":
            name = "LevelCity - Day"
        elif title == "City (Night)":
            name = "LevelCity - Night"
        else:
            name = "Test Zone"

        # TODO remove this once the message passing are completed
        agents = list()
        for agent_data in data["world"]["agents"]:
            user_data = agent_data["user"]
            if user_data["username"] is None:
                username = "{0} {1}".format(
                    user_data["nameFirst"], user_data["nameLast"]
                )
            else:
                username = user_data["username"]
            agent = self.__create_agent(
                self.__create_user(username=username),
                UnityCharacter(**agent_data["character"])
                if "character" in agent_data
                else None,
                UnityTransform(**agent_data["transform"])
                if "transform" in agent_data
                else None,
            )
            agents.append(agent)

        scene = OutDataScene(
            name=name,
            title=title,
            agents=[OutDataAgent(**agent.dict()) for agent in agents],
        )
        self._current_scene_identifier = scene
        self._unity_agent_player_manager.add_agents(agents)
        return scene

    def register_agents(self, scene: OutDataScene):
        for agent in scene.agents:
            self._unity_agent_player_manager.add_agent(UnityAgent(**agent.model_dump()))

    # Wrappers to not expose UnityAgentPlayerManager
    # TODO: Clean this up later
    def get_agent(self, agent_id: str) -> UnityAgent:
        return self._unity_agent_player_manager.get_agent(agent_id)

    def get_player(self, player_id: str) -> UnityAgent:
        return self._unity_agent_player_manager.get_player(player_id)

    def add_player(self, player: UnityPlayer) -> bool:
        return self._unity_agent_player_manager.add_player(player)

    def update_player(self, player: UnityPlayer) -> bool:
        return self._unity_agent_player_manager.update_player(player)

    def remove_player(self, player_id: str) -> bool:
        return self._unity_agent_player_manager.remove_player(player_id)

    def get_players(self, player_id_list: List[str]) -> List[UnityPlayer]:
        return self._unity_agent_player_manager.get_players(player_id_list)

    def get_agents(self, agent_id_list: List[str]) -> List[UnityAgent]:
        return self._unity_agent_player_manager.get_agents(agent_id_list)

    def get_agent_id_list(self) -> List[UnityAgent]:
        return self._unity_agent_player_manager.get_agent_id_list()

    def username_to_id(self, username: str) -> str:
        return self._unity_agent_player_manager.username_to_id(username)

    def player_usernames(self) -> List[str]:
        return self._unity_agent_player_manager.player_usernames

    def agent_usernames(self) -> List[str]:
        return self._unity_agent_player_manager.agent_usernames

    def get_player_id_list(self) -> List[str]:
        return self._unity_agent_player_manager.get_player_id_list()
