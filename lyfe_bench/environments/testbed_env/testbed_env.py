"""A simple conversation environment using pettingzoo.

Built using https://pettingzoo.farama.org/content/environment_creation/

Note that ML-agents use an old version of pettingzoo <=1.21 (with major API difference)
"""

import logging
import time

import numpy as np

# from gym.spaces import Text, Dict

from lyfe_bench.environments.testbed_env.maps.map_aliases import (
    big_example_map,
    example_map,
    no_place_map,
)
from lyfe_bench.utils.messaging.messaging import (
    MessagingSystem,
    TalkSystem,
)
from lyfe_bench.utils.messaging.location_system import (
    LocationSystem,
    EntityLocations,
    NearbyCreature,
    ObservableEntitiesSystem,
)

# from lyfe_bench.utils.world_time import world_time_update, world_time_format_str
from lyfe_bench.utils.world_time import WorldTime
from lyfe_bench.utils.logging import get_colored_text

logger = logging.getLogger(__name__)

color_codes = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "default": "\033[0m",  # Resets the color
}


# WorldTimeVars = namedtuple("WorldTime", ["year", "month", "day", "hour"])
# default_world_time = WorldTimeVars(2020, 1, 1, 7)
default_world_time = "01/01/2020 07:00:00"


class GraphEnv:
    """Graph environment for conversation and graph-based navigation.

    This GraphEnv allows agents to navigate a graph of locations and communicate with each other.

    The metadata holds environment constants. From gymnasium, we inherit the "render_modes",
    metadata which specifies which modes can be put into the render() method.
    At least human mode should be supported.
    The "name" metadata allows the environment to be pretty printed.
    """

    metadata = {"render_modes": ["human"], "name": "testbed_env"}
    maps = {
        "big_example": big_example_map,
        "example": example_map,
        "no_place": no_place_map,
    }

    def __init__(
        self,
        agents,
        name="world",
        frame_rate: int = 60,  # TODO: remove frame_rate from Env
        time_multiplier: int = 20,
        world_time=default_world_time,
        map=None,
        **kwargs,
    ):
        self.agents = agents
        self.agent_name_mapping = dict(zip(self.agents, list(range(len(self.agents)))))
        self.timer = {agent: 0 for agent in self.agents}
        self.name = name

        # # gymnasium spaces are defined and documented here: https://gymnasium.farama.org/api/spaces/
        # action_space = Dict({"message": Text(max_length=1000)})
        # observation_space = Dict({"message": Text(max_length=1000)})
        # self.render_mode = render_mode

        # To implement fix rate sampling of the env
        self.frame_rate = frame_rate
        self.start_time = time.perf_counter()

        # To implement world time
        self.world_time = WorldTime(world_time)
        self.time_multiplier = time_multiplier

        # Environment detail system
        self.environment_details_system = MessagingSystem()
        # Messaging system
        self.message_system = MessagingSystem()
        # Item system
        self.item_system = MessagingSystem()
        # Talk systems
        self.talk_system = TalkSystem()
        # Location-related attributes and systems
        if map is None or map == "no_place":
            map = self.maps["no_place"]
            map.add_node(self.name)
        elif isinstance(map, str):
            assert map in self.maps, f"Map {map} not found"
            map = self.maps[map]
        self.map_graph = map
        self.nearby_creature = NearbyCreature(self.agents)
        self.entity_locations = EntityLocations(
            entities=self.agents, graph=self.map_graph
        )
        self.observable_entities_system = ObservableEntitiesSystem(
            entity_locations=self.entity_locations,
            nearby_creature=self.nearby_creature,
            graph=self.map_graph,
        )
        self.locations = list(self.map_graph.nodes)
        self.location_system = LocationSystem(
            entity_locations=self.entity_locations,
            nearby_creature=self.nearby_creature,
            graph=self.map_graph,
            world_time=self.world_time,
        )

        # for debugging
        self._cycle_end_time = time.time()

    # # this cache ensures that same space object is returned for the same agent
    # # allows action space seeding to work as expected
    # @functools.lru_cache(maxsize=None)
    # def observation_space(self, agent):
    #     # gymnasium spaces are defined and documented here: https://gymnasium.farama.org/api/spaces/
    #     return Dict(
    #         {
    #             "time": Text(max_length=1000),
    #             "message": Text(max_length=1000),  # message
    #             "talk": Text(max_length=1000),
    #         }
    #     )

    # @functools.lru_cache(maxsize=None)
    # def action_space(self, agent):
    #     return Dict(
    #         {
    #             "message": tuple((Text(max_length=1000), Text(max_length=1000))),
    #             "talk": Text(max_length=1000),
    #         }
    #     )

    # TODO: Why is this not the same as pettingzoo??
    def get_observations(self, agent_index):
        """
        Observe should return the observation of the specified agent. This function
        should return a sane observation (though not necessarily the most up to date possible)
        at any time after reset() is called.
        """
        agent = self.agents[agent_index]

        env_detail_received = self.environment_details_system.receive_messages(agent)
        obs_env_detail = (
            self._preprocess_environment_details(env_detail_received)
            if env_detail_received
            else None
        )

        # Receive message from other agents
        messages_received = self.message_system.receive_messages(agent)
        obs_msg = (
            self._preprocess_messages(messages_received) if messages_received else None
        )

        item_received = self.item_system.receive_messages(agent)
        obs_receive = self._preprocess_item(item_received) if item_received else None

        talk_received = self.talk_system.receive_messages(agent)
        obs_talk = self._preprocess_talk(talk_received) if talk_received else None

        arrival_received = self.location_system.receive_messages(agent)
        obs_arrival = arrival_received if arrival_received else None

        observable_entities_received = self.observable_entities_system.receive_messages(
            agent
        )
        obs_observable_entities = observable_entities_received

        # additional observations
        nearby_creature = self.nearby_creature(agent)

        # observation of one agent is the previous state of the other
        obs = {
            "time": self.world_time.format_str("%m/%d %H:%M"),
            "visible_creatures": frozenset(),
            "message": obs_msg,
            "item": obs_receive,
            "talk": obs_talk,
            "move_ended": obs_arrival,
            "nearby_creature": nearby_creature,
            "locations": self.locations,  # only needed at the very beginning
            "observable_entities": obs_observable_entities,
            "environment_details": obs_env_detail,
        }

        return obs

    def reset(self, seed=None, options=None):
        # timer calculates the step on the agent
        self.timer = {agent: 0 for agent in self.agents}
        # receiver stores the agent that this agent messages to since last reset
        self.receiver = {agent: [] for agent in self.agents}

        self.start_time = time.perf_counter()

        # Providing detail on environment
        for agent in self.agents.values():
            self.environment_details_system.send_message("ENV", agent, "basic")

    # TODO: Why is this not the same as pettingzoo??
    def set_action(self, agent_index, action):
        agent = self.agents[agent_index]
        # do information transfer
        if action.get("message") is not None:
            self._message_step(agent, action)
        if action.get("send") is not None:
            self._send_step(agent, action)
        if action.get("talk") is not None:
            self._talk_step(agent, action)
        if action.get("choose_destination") is not None:
            self.location_system.send_message(agent, action["choose_destination"])
        if action.get("expressions") is not None:
            self.observable_entities_system.send_message(agent, action["expressions"])

        self.timer[agent] += 1

    def _preprocess_messages(self, received_obj):
        msg_list = []
        for sender, content in received_obj:
            processed_content = (
                content if sender is None else f"{sender} messages me: {content}"
            )
            msg_list.append(processed_content)
        return "\n".join(msg_list)

    def _preprocess_item(self, received_obj):
        item_list = []
        for sender, content in received_obj:
            processed_content = content if not sender else {sender: content}
            item_list.append(processed_content)
        return item_list

    def _preprocess_talk(self, received_obj):
        sender, content = received_obj
        return f"{sender} says: {content}"

    def _preprocess_environment_details(self, received_obj):
        _, _, env_detail = received_obj
        return env_detail

    def _message_step(self, agent, action):
        # Adding a conversation threshold
        # TODO: related to the num_agents, TEMPORARY

        threshold = 200
        if self.timer[agent] > threshold and len(np.unique(self.receiver[agent])) < 2:
            self.dones[agent] = True

        # Send message to other agents
        # message is a tuple(str, str) of (receiver, message)

        message = action["message"]
        receiver, message_sent = message

        # update state
        self.receiver[agent].append(receiver)

        if receiver != "[NONE]":
            # set receiver to alive if it is dead
            self.dones[receiver] = False
            self.timer[receiver] = 0
            self.receiver[self.agent_selection] = []
        if message_sent != "[NONE]":
            self.message_system.send_message(agent, receiver, message_sent)
            self.dones[agent] = False

    def _send_step(self, agent, action):
        if len(action["send"]):
            receiver, item, number = (
                action["send"][0],
                action["send"][1].split(":")[0],
                int(action["send"][1].split(":")[1]),
            )
            self.item_system.send_message(agent, receiver, {item: number})

    def _talk_step(self, agent, action):
        if len(action["talk"]):
            for receiver in self.nearby_creature(agent):
                talk = action["talk"]
                self.talk_system.send_message(agent, receiver, talk)

    def time_update(self):
        # state updates here
        self.location_system.update()

        max_time = 1.0 / self.frame_rate
        # Simulate fixed frame rate
        elapsed_time = time.perf_counter() - self.start_time
        time.sleep(max(max_time - elapsed_time, 0))
        self.start_time = time.perf_counter()

        # Logging
        logger.debug(f"Cycle time: {time.time() - self._cycle_end_time:.3f} s")
        # Update the world time
        self.world_time += self.time_multiplier * (time.time() - self._cycle_end_time)

        self._cycle_end_time = time.time()

    def wait_until_ready(self, timeout):
        pass

    def close(self):
        """
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user is no longer using the environment.
        """
        pass
