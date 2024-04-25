import logging
import time

from datetime import datetime
from typing import List

from lyfe_python_env import BaseProfilingClass

from lyfe_agent.utils.log_utils import log_message
from lyfe_agent.utils.name_utils import (
    name_lower2higher,
    name_match,
)
from lyfe_agent.datatype.send_in import (
    SEND_IN_AGENT_CHAT_MESSAGE,
    SEND_IN_AGENT_DIRECT_MESSAGE,
    SEND_IN_AGENT_FEEDBACK,
    SEND_IN_AGENT_MOVE_ENDED,
    SEND_IN_CHARACTER_PROXIMITY,
    SEND_IN_PLAYER_ADDED,
    SEND_IN_PLAYER_CHAT_MESSAGE,
    SEND_IN_PLAYER_DIRECT_MESSAGE,
    SEND_IN_PLAYER_REMOVED,
    SendIn,
    SendInAgentFeedback,
)
from lyfe_agent.datatype.send_out import (
    SendOutAgentChatMessage,
    SendOutAgentCodeMessage,
    SendOutAgentDirectMessage,
    SendOutAgentMoveLocation,
    SendOutAgentMoveStop,
    SendOutObjectInstantiation,
    SendOutCharacterEmote,
    SendOutCharacterLookAt,
    SendOutTask,
    EmoteKind,
)
from lyfe_agent.environments.environment_utils import (
    world_time_update,
    world_time_format_str,
)

logger = logging.getLogger(__name__)


def log_event(
    event_type: str,
    user_type: str,
    user_id: str,
    username: str,
    observation_type: str,
    extra_info: dict = None,
):
    info = {
        "event_type": event_type,
        "user_type": user_type,
        "user_id": user_id,
        "username": username,
        "observation_type": observation_type,
    }
    if extra_info is not None:
        info.update(extra_info)

    msgs = [f"\n\t{key}: {value}" for key, value in info.items()]
    # logger.debug(f"{' '.join(msgs)}")
    logger.debug(f"{' '.join(msgs)}")


class ExternalEnvWrapper(BaseProfilingClass):
    """Wrapper that handles communication through websockets."""

    def __init__(
        self,
        web_socket_env,
        agent_names,
        env_dict: dict[str, str],
        frame_rate: int = 30,
        sim_speed: int = 100,
        world_time=None,
        enable_monitoring=False,
    ):
        BaseProfilingClass.__init__(self, enable_monitoring=enable_monitoring)
        self.last_move = [None for _ in range(len(agent_names))]

        # To implement world time
        self.world_time = datetime(
            year=world_time.year,
            month=world_time.month,
            day=world_time.day,
            hour=world_time.hour,
        )
        self._sim_speed = sim_speed / frame_rate

        self.agent_names = agent_names
        self.web_socket_env = web_socket_env

        # TEMP: to be moved to agent
        self.unity_resource = self.web_socket_env.get_unity_resources()
        self.id_to_agent_name = {
            id: self.unity_resource.get_agent(id).user.username
            for id in self.unity_resource.get_agent_id_list()
        }
        self.id_list = self.unity_resource.get_agent_id_list()

        # Mappings
        # This will need to be modified if players can join before sim starts
        self.id_to_player_name = {}
        self.nearby_creatures = {id: [] for id in self.id_to_agent_name.keys()}
        self.visible_creatures = {id: [] for id in self.id_to_agent_name.keys()}
        self.locations = {id: [] for id in self.id_to_agent_name.keys()}

        assert env_dict is not None, "env_dict must be provided"
        self.nonce = env_dict["NONCE"]

        # Handles those things that are observable to other agents
        self.agent_expressions = {id: {} for id in self.id_to_agent_name.keys()}

    @property
    def id_to_name(self):
        return self.id_to_agent_name | self.id_to_player_name

    @property
    def name_to_id(self):
        return {v: k for k, v in self.id_to_name.items()}

    def convert_action(self, action, agent_id):
        """Converts the action from the Python agent to the Unity agent.

        AI (Python)->Environment (Unity)
        """
        data = []

        # This is the latest way to send unity commands
        task_commands = []
        action_chat_message: str = action.get("talk", None)
        if action_chat_message is not None:
            data.append(
                SendOutAgentChatMessage(agentId=agent_id, message=action_chat_message)
            )

        action_code_message: str = action.get("code", None)
        if action_code_message is not None:
            data.append(
                SendOutAgentCodeMessage(agentId=agent_id, message=action_code_message)
            )

        # TODO: Actually provide anim in action. Currently, if there is a chat message, talk would be True
        if action_chat_message is not None:
            task_commands.append(
                SendOutCharacterEmote(
                    userId=agent_id,
                    emoteId=EmoteKind.Talking,
                    emoteActive=True,
                    emotePlayTime=1.0
                    if action_chat_message is None
                    else len(action_chat_message) / 10.0,
                )
            )

        action_look_at: str = action.get("look_at", None)
        if action_look_at is not None:
            task_commands.append(
                SendOutCharacterLookAt(
                    userId=agent_id,
                    targetEntityId=action_look_at,
                )
            )
        action_stop_moving: bool = action.get("stop_moving", False)
        if action_stop_moving:
            task_commands.append(SendOutAgentMoveStop(agentId=agent_id))

        action_dm = action.get("message", None)
        if action_dm is not None:
            action_dm_message, action_dm_receiver_username = action_dm
            receiverId = self.name_to_id[action_dm_receiver_username]
            logger.info(f"receiverId: {receiverId}")
            if receiverId is not None:
                data.append(
                    SendOutAgentDirectMessage(
                        agentId=agent_id,
                        message=action_dm_message,
                        receiverId=receiverId,
                    )
                )
                task_commands.append(
                    SendOutCharacterEmote(
                        userId=agent_id,
                        emoteId=EmoteKind.PhoneCall,
                        emoteActive=True,
                    )
                )

        action_move_location: str = action.get("choose_destination", None)
        if action_move_location is not None:
            data.append(
                SendOutAgentMoveLocation(
                    agentId=agent_id, location=action_move_location
                )
            )

        action_instantiate_object = action.get("instantiate_object", None)
        if action_instantiate_object is not None:
            data.append(
                SendOutObjectInstantiation(
                    agentId=agent_id,
                    objectType=action_instantiate_object.get("objectType", None),
                    transform=action_instantiate_object.get("transform", None),
                )
            )

        if len(task_commands) > 0:
            task_id = "task_{0}_{1}".format(agent_id, time.time())
            data.append(
                SendOutTask(
                    taskId=task_id,
                    waitForResponse=False,
                    commands=task_commands,
                )
            )

        return data

    def set_action(self, agent_index, action: dict):
        """Change text action into int."""
        new_action = dict()

        # Handle expressions
        self.agent_expressions[self.id_list[agent_index]] = action.get(
            "expressions", {}
        )

        choose_destination = action.get("choose_destination", None)
        if choose_destination == "arrival":
            self.last_move[agent_index] = "arrival"
        elif choose_destination is not None:
            if choose_destination != self.last_move[agent_index]:
                self.last_move[agent_index] = choose_destination
                new_action["choose_destination"] = self.last_move[agent_index]

        # Talk
        new_action["talk"] = action.get("talk", None)
        if action.get("look_at", None) is not None:
            new_action["look_at"] = action["look_at"]
        if action.get("stop_moving", None) is not None:
            new_action["stop_moving"] = action["stop_moving"]

        # Code
        new_action["code"] = action.get("code", None)

        if new_action.get("message", None) is not None:
            logger.debug(
                log_message(
                    self.agent_names[agent_index],
                    "MESSAGE",
                    new_action["message"],
                    world_time_format_str(self.world_time),
                )
            )
        if new_action.get("choose_destination", None) is not None:
            logger.debug(
                log_message(
                    self.agent_names[agent_index],
                    "MOVE",
                    new_action["choose_destination"],
                    world_time_format_str(self.world_time),
                )
            )
        if new_action.get("talk", None) is not None:
            logger.debug(
                log_message(
                    self.agent_names[agent_index],
                    "TALK",
                    new_action["talk"],
                    world_time_format_str(self.world_time),
                )
            )

        # # # TODO: refactoring convert action
        action_data = self.convert_action(new_action, self.id_list[agent_index])

        for action_item in action_data:
            self.web_socket_env.send_action(action_item)

    def time_update(self):
        self.world_time = self.world_time_update()
        # Simulate MLAgent's latency by sleeping for 5ms, otherwise the simulation is too fast
        time.sleep(0.005)

    def __process_agent_messages_handler_agent_chat_message(self, observation, data):
        message = data.message
        name = self.id_to_agent_name[data.agentId]
        talk = f"{name} says: {message}"
        observation["talk"] = talk
        # Hacky way to support looking at someone who is talking
        observation["talk_structured"] = {
            "character_id": data.agentId,
            "message": message,
        }

        extra_info = {"observation": f"{name} says: {message}"}
        log_event("OBSERVATION", "AGENT", data.agentId, name, "talk", extra_info)

    def __process_agent_messages_handler_agent_direct_message(self, observation, data):
        message = data.message
        name = self.id_to_agent_name[data.agentId]
        message = f"{name} direct messages me: {message}"
        observation["message"] = message

        extra_info = {"observation": f"{name} direct messages me: {message}"}
        log_event("OBSERVATION", "AGENT", data.agentId, name, "message", extra_info)

    def __process_agent_messages_handler_player_chat_message(self, observation, data):
        player_id = data.playerId
        if self.id_to_player_name.get(player_id, None) is None:
            logger.warning(f"Player with id '{player_id}' not found")
            return
        player_name = self.id_to_player_name[player_id]

        message: str = data.message
        # TODO: Should be made more general by having less pre-processing
        talk: str = f"{player_name} says: {message}"
        observation["talk"] = talk
        # Hacky way to support looking at someone who is talking
        observation["talk_structured"] = {"character_id": player_id, "message": message}

        extra_info = {"observation": f"{player_name} says: {message}"}
        log_event("OBSERVATION", "PLAYER", player_id, player_name, "talk", extra_info)

    def __process_agent_messages_handler_player_direct_message(self, observation, data):
        player_id = data.playerId
        if self.id_to_player_name.get(player_id, None) is None:
            logger.warning(f"Player with id '{player_id}' not found")
            return
        player_name = self.id_to_player_name[player_id]

        message: str = f"{player_name} direct messages me: {data.message}"
        observation["message"] = message

        extra_info = {
            "observation": f"{player_name} direct messages me: {data.message}"
        }
        log_event(
            "OBSERVATION", "PLAYER", player_id, player_name, "message", extra_info
        )

    def __process_agent_messages_handler_move_ended(self, observation, data):
        agent_id = data.agentId
        name = self.id_to_agent_name[agent_id]
        observation["move_ended"] = data.arrivalDestination

        extra_info = {"destination": data.arrivalDestination}
        log_event("OBSERVATION", "AGENT", agent_id, name, "move_ended", extra_info)

    def __process_agent_messages_handler_player_joined(self, observation, data):
        observation["player_joined"] = data.username
        self.id_to_player_name[data.playerId] = data.username
        log_event(
            "OBSERVATION", "PLAYER", data.playerId, data.username, "player_joined"
        )

    def __process_agent_messages_handler_player_removed(self, observation, data):
        player_id = data.playerId
        player_name = self.id_to_player_name.get(player_id, None)
        if player_name is not None:
            observation["player_removed"] = player_name
            log_event("OBSERVATION", "PLAYER", player_id, player_name, "player_removed")
            self.id_to_player_name.pop(data.playerId)

    def __process_agent_messages_handler_character_proximity(self, observation, data):
        # # for players
        # transform = data.transform
        # nearby_players = data.near_by.players
        # nearby_agents = data.near_by.agents
        # nearby_locations = data.near_by.locations

        transform = data.transform
        nearby_players = data.nearBy.players
        nearby_agents = data.nearBy.agents
        nearby_locations = data.nearBy.locations
        if data.visibility is None:
            visible_players = []
            visible_agents = []
        else:
            visible_players = data.visibility.players
            visible_agents = data.visibility.agents

        observation["nearby_creature"] = [
            creature
            for creature in [self.id_to_player_name.get(p) for p in nearby_players]
            + [self.id_to_agent_name.get(a) for a in nearby_agents]
            if creature is not None
        ]
        observation["locations"] = nearby_locations
        observation["visible_creature"] = [
            creature
            for creature in [self.id_to_player_name.get(p) for p in visible_players]
            + [self.id_to_agent_name.get(a) for a in visible_agents]
            if creature is not None
        ]

        self.nearby_creatures[data.agentId] = observation["nearby_creature"].copy()
        self.visible_creatures[data.agentId] = observation["visible_creature"].copy()
        self.locations[data.agentId] = observation["locations"].copy()

    def __process_agent_messages_handler_agent_feedback(
        self, observation, data: SendInAgentFeedback
    ):
        agent_id = data.agentId
        name = self.id_to_agent_name[agent_id]
        observation["general"] = data.message

        extra_info = {"general": data.message}
        log_event("OBSERVATION", "AGENT", agent_id, name, "general", extra_info)

    def process_agent_messages(self, agent_id, raw_data: List[SendIn]):
        # agent_name = self.agent_names[agent_id]
        observation = dict()
        env_time = None

        for data in raw_data:
            # get env time
            if hasattr(data, "envTime"):
                env_time = data.envTime

            # process messages
            if data.messageType == SEND_IN_AGENT_CHAT_MESSAGE:
                self.__process_agent_messages_handler_agent_chat_message(
                    observation, data
                )
            elif data.messageType == SEND_IN_AGENT_DIRECT_MESSAGE:
                self.__process_agent_messages_handler_agent_direct_message(
                    observation, data
                )
            elif data.messageType == SEND_IN_PLAYER_CHAT_MESSAGE:
                self.__process_agent_messages_handler_player_chat_message(
                    observation, data
                )
            elif data.messageType == SEND_IN_PLAYER_DIRECT_MESSAGE:
                self.__process_agent_messages_handler_player_direct_message(
                    observation, data
                )
            elif data.messageType == SEND_IN_AGENT_MOVE_ENDED:
                self.__process_agent_messages_handler_move_ended(observation, data)
            elif data.messageType == SEND_IN_PLAYER_ADDED:
                self.__process_agent_messages_handler_player_joined(observation, data)
            elif data.messageType == SEND_IN_PLAYER_REMOVED:
                self.__process_agent_messages_handler_player_removed(observation, data)
            elif data.messageType == SEND_IN_CHARACTER_PROXIMITY:
                self.__process_agent_messages_handler_character_proximity(
                    observation, data
                )
            elif data.messageType == SEND_IN_AGENT_FEEDBACK:
                self.__process_agent_messages_handler_agent_feedback(observation, data)

        observation.update(
            {
                "env_time": env_time,
                "nearby_creature": self.nearby_creatures[self.id_list[agent_id]],
                "visible_creature": self.visible_creatures[self.id_list[agent_id]],
                "locations": self.locations[self.id_list[agent_id]],
                "contacts": {
                    "agent_usernames": list(self.id_to_agent_name.values()),
                    "player_usernames": list(self.id_to_player_name.values()),
                },
            }
        )

        return observation

    def get_observations(self, agent_index):
        """Pre-process observation from Unity to provide to the Python agents."""
        raw_data = self.web_socket_env.get_observations(
            self.web_socket_env.get_agent_id_list()[agent_index]
        )

        obs = self.process_agent_messages(agent_index, raw_data)

        # Important for data collection
        evaluation_monitor = False
        # format : "someone says: something"
        obs_chat = obs.get("talk", None)
        if obs_chat not in self.nonce:
            sender_name = obs_chat.split(" says:")[0]
            # This name_match is to deal with names with dash (e.g. Fatima Al-Khouri, whose unity display name is 'Fatima Al Khouri')
            is_matched, _ = name_match(sender_name, self.agent_names, threshold=0.9)
            if not is_matched:  # If sender is not an agent
                evaluation_monitor = True
                logger.info(
                    log_message(
                        sender_name,
                        "TALK",
                        obs_chat,
                        world_time_format_str(self.world_time),
                    )
                )
        else:
            obs_chat = None

        # original format: "name1;name2;name3"
        nearby_creature = obs.get("nearby_creature", [])
        nearby_creature = [name_lower2higher(n) for n in nearby_creature]
        # TODO: may actually want this to be under visible_creature
        expressions = {
            name: self.agent_expressions.get(self.name_to_id.get(name), {})
            for name in nearby_creature
        }

        # format: "name1;name2;name3"
        visible_creature = obs.get("visible_creature", [])
        visible_creature = frozenset([name_lower2higher(n) for n in visible_creature])

        # TODO: Need a simplification, this is too complicated, and hard for people to understand
        # TODO: It's also not clear what the types of each observation are
        return {
            "time": world_time_format_str(self.world_time),
            "locations": obs.get("locations", None),
            "move_ended": obs.get("move_ended", None),
            "talk": obs_chat,
            "nearby_creature": nearby_creature,
            "visible_creatures": visible_creature,
            "evaluation_monitor": evaluation_monitor,
            "contacts": obs.get("contacts", None),
            "observable_entities": expressions,
            # Hacky way to support looking at someone who is talking
            "talk_structured": obs.get("talk_structured", None),
            "general": obs.get("general", None),
        }

    def world_time_update(self):
        """Update the world time. World time is sim_speed X faster than real time."""
        return world_time_update(self.world_time, self._sim_speed)

    def plot_timings(self):
        super().plot_timings()
        self.web_socket_env.plot_timings()

    def get_agent_names(self):
        return self.agent_names

    def close(self):
        self.web_socket_env.close()

    def wait_until_ready(self, timeout=60):
        # Wait at most 60 seconds for incoming messages
        current_time = time.time()
        while self.web_socket_env.get_incoming_message_count() == 0:
            if time.time() - current_time > timeout:
                raise TimeoutError(
                    f"Waited for {timeout} seconds but no incoming messages received."
                )
            time.sleep(0.1)


def process_content(sender, content, communication_type):
    if not sender:
        return content
    processed_content = sender
    processed_item = dict()
    if communication_type == "message":
        processed_content += " messages me: "
    # item receive is in the form of {sender: {item1: number1}, {item2: number2}}
    elif communication_type == "item":
        processed_item[sender] = content
        return processed_item
    processed_content += content + "\n"
    return processed_content
