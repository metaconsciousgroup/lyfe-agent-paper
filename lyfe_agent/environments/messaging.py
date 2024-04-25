"""Simple system for handling direct messaging between agents."""

import logging
import networkx as nx
import random
from collections import deque

from typing import List, Optional, Union

logger = logging.getLogger(__name__)


class MessagingSystem:
    def __init__(self):
        """
        Initializes a new MessagingSystem instance with an empty message dictionary.
        """
        self.messages = {}

    def send_message(self, sender, receiver, message):
        """
        Sends a message from the sender to the receiver.

        Args:
            sender (str): The username of the sender.
            receiver (str): The username of the receiver.
            message (Any): The message to send.
        """
        if receiver not in self.messages:
            self.messages[receiver] = []

        self.messages[receiver].append((sender, message))

    def receive_messages(self, receiver):
        """
        Retrieves all messages sent to the receiver and removes them from the system.

        Args:
            receiver (str): The username of the receiver.

        Returns:
            list: A list of tuples containing the sender and message for each message.
        """
        if receiver not in self.messages:
            return []

        messages = self.messages[receiver]
        del self.messages[receiver]

        return messages

class TalkSystem:
    def __init__(self):
        """
        Initializes a new MessagingSystem instance with an empty message dictionary.
        """
        self.messages = {}

    def send_message(self, sender, receiver, message):
        """
        Sends a message from the sender to the receiver.

        Args:
            sender (str): The username of the sender.
            receiver (str): The username of the receiver.
            message (Any): The message to send.
        """
        if receiver not in self.messages:
            self.messages[receiver] = deque()

        self.messages[receiver].append((sender, message))

    def receive_messages(self, receiver):
        """
        Retrieves the oldest message sent to the receiver and removes it from the system.

        Args:
            receiver (str): The username of the receiver.

        Returns:
            tuple: A tuple containing the sender and message.
        """
        if receiver not in self.messages or not self.messages[receiver]:
            return None

        message = self.messages[receiver].popleft()

        # If the deque becomes empty after popping, we can delete the key from the dictionary
        if not self.messages[receiver]:
            del self.messages[receiver]

        return message


class NearbyCreature:
    def __init__(self, agents):
        self.agents = agents
        self.data = {agent: [a for a in self.agents if a != agent] for agent in agents}

    def __call__(self, agent):
        return self.data[agent]


class LocationSystem:
    def __init__(
        self,
        entities: Union[List[str], dict[str, str]],
        nearby_creature: NearbyCreature,
        graph: Optional[nx.Graph] = None,
    ):
        if graph is None:
            self.graph = nx.Graph()
            self.graph.add_node("world")
        else:
            self.graph = graph
            # if edges don't have edge weights, assume that travel time is 0
            for _, _, data in self.graph.edges(data=True):
                if "weight" not in data:
                    data["weight"] = 0
        self.nodes = list(self.graph.nodes())
        self.edges = list(self.graph.edges())
        # assume that entities are instantiated at random locations
        if isinstance(entities, list):
            self.entity_locations = {
                entity: random.choice(self.nodes) for entity in entities
            }
        elif isinstance(entities, dict):
            self.entity_locations = entities
        else:
            self.entity_locations = {}
            logger.warn("entities must be a list or a dictionary, using empty dictionary")
        self.entities = list(self.entity_locations.keys())
        self.nearby_creature = nearby_creature
        # initialize position of nearby creatures
        self.update_nearby_creatures()

        # for storing agent movements
        self.movement = {}
        # for providing arrival signals
        self.messages = {}

    def accessible_locations(self, node):
        return self.graph.neighbors(node)

    def store_entity_location(self, entity, location):
        self.entity_locations[entity] = location
        self.update_nearby_creatures()

    def get_entity_location(self, entity):
        return self.entity_locations[entity]

    def update_nearby_creatures(self):
        self.nearby_creature.data = {
            entity: [
                a
                for a in self.entities
                if self.entity_locations[a] == self.entity_locations[entity]
                and a != entity
                and self.entity_locations[a] is not None
            ]
            for entity in self.entities
        }

    def update(self):
        # generate an arrival signal for each entity
        dropped_entities = []
        for entity, movement_info in self.movement.items():
            movement_info["time_to_arrival"] -= 1
            if movement_info["time_to_arrival"] < 0:
                self.store_entity_location(entity, movement_info["destination"])
                dropped_entities.append(entity)
                # arrival signal
                self.messages[entity] = movement_info["destination"]
        for entity in dropped_entities:
            del self.movement[entity]

    def send_message(self, entity, destination):
        """
        If an agent decides to move, this is the function to call.
        """
        origin = self.entity_locations[entity]
        travel_time = self.graph[origin][destination]["weight"]
        self.movement[entity] = {
            "origin": origin,
            "destination": destination,
            "time_to_arrival": travel_time,
        }
        self.store_entity_location(entity, None)

    def receive_messages(self, entity):
        """
        Returns any arrival signals
        """
        if entity not in self.messages.keys():
            return None
        else:
            message = self.messages[entity]
            del self.messages[entity]
            return message
