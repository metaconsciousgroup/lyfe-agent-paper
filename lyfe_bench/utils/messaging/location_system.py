import logging
import networkx as nx
import random

from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)


class NearbyCreature:
    def __init__(self, agents: List[str]):
        self.agents = agents
        self.data = {
            agent: [a for a in self.agents if a != agent]
            for agent in agents
        }

    def __call__(self, agent: str):
        return self.data[agent]

class EntityLocations:
    """
    A container for all the locations of each entity, updated by `LocationSystem`.
    Separate from `LocationSystem` to allow for access by other systems.
    """
    def __init__(self, entities: List[str], graph: nx.Graph):
        self.graph = graph
        self.nodes = list(self.graph.nodes())
        self.edges = list(self.graph.edges())
        # assume that entities are instantiated at random locations
        if isinstance(entities, list):
            self.data = {entity: random.choice(self.nodes) for entity in entities}
        elif isinstance(entities, dict):
            self.data = entities
        else:
            raise ValueError("entities must be a list or a dictionary")

        self.entities = list(self.data.keys())

    def update(self, entity: str, location: str):
        self.data[entity] = location

    def __call__(self, entity):
        return self.data[entity]

class ObservableEntitiesSystem:
    def __init__(self, entity_locations: EntityLocations, nearby_creature: NearbyCreature, graph: nx.Graph):
        self.entity_locations = entity_locations
        self.entities = self.entity_locations.entities
        self.nearby_creature = nearby_creature
        self.graph = graph
        self.data = {entity: {} for entity in self.entities}

    def __call__(self, entity):
        return self.data[entity]
    
    def send_message(self, sender: str, message: str):
        """
        Note that there is no receiver
        """
        # print("data: ", self.data)
        self.data[sender] = message

    def receive_messages(self, receiver: str):
        observables = {entity: expression for entity, expression in self.data.items() if entity in self.nearby_creature(receiver)}
        return observables


class LocationSystem:
    """
    Manages updating `EntityLocations`, enacting any movement rules specified by the map graph.
    """
    def __init__(
        self,
        entity_locations: EntityLocations,
        nearby_creature: NearbyCreature,
        graph: Optional[nx.Graph] = None,
        world_time: Optional[datetime] = None,
    ):
        """
        entity_locations: Core object that is updated
        nearby_creature: Auxiliary class updated along with entity_locations
        graph: Tracks the graphical structure of the environment
        world_time: Optional argument which is used to record trajectories
        """
        if graph is None:
            self.graph = nx.Graph()
            self.graph.add_node("world")
        else:
            self.graph = graph
            # if edges don't have edge weights, assume that travel time is 0
            for _, _, data in self.graph.edges(data=True):
                if "travel_time" not in data:
                    data["travel_time"] = data["weight"]
                    data["vision"] = 0
                    data["auditory"] = 0
        self.nodes = list(self.graph.nodes())
        self.edges = list(self.graph.edges())
        # assume that entities are instantiated at random locations
        # self.entity_locations = EntityLocations(entities, self.graph) # TODO
        self.entity_locations = entity_locations

        self.entities = self.entity_locations.entities
        self.nearby_creature = nearby_creature
        # initialize position of nearby creatures
        self.update_nearby_creatures()

        # for tracking moving agents
        self.movement = {}
        # for providing arrival signals
        self.messages = {}
        # for recording trajectories
        self.world_time = world_time
        if self.world_time is not None:
            self.history = {
                entity: [(self.world_time.format_str(), location)]
                for entity, location in self.entity_locations.data.items()
            }
        
    def accessible_locations(self, node):
        return self.graph.neighbors(node)

    def store_entity_location(self, entity, location):
        self.entity_locations.update(entity, location)
        logger.info(f"{entity} is now at {location}")

        self.update_history(entity, location)
        self.update_nearby_creatures()

    def store_entity_in_transit(self, entity, origin, destination):
        self.entity_locations.update(entity, None)
        logger.info(f"{entity} is now in transit from {origin} to {destination}")

        self.update_history(entity, f"moving from {origin} to {destination}")
        self.update_nearby_creatures()
    
    def get_entity_location(self, entity):
        return self.entity_locations(entity)
    
    def update_nearby_creatures(self):
        self.nearby_creature.data = {
            entity: [a for a in self.entities
                     if self.entity_locations(a) == self.entity_locations(entity)
                     and a != entity and self.entity_locations(a) is not None]
            for entity in self.entities
        }

    def update_history(self, entity, location):
        """
        Updates the history of an entity's location.
        """
        if self.world_time is not None:
            self.history[entity].append((self.world_time.format_str(), location))

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
        origin = self.entity_locations(entity)
        if origin == destination:
            travel_time = 0
        else:
            travel_time = self.graph[origin][destination]["travel_time"]
        self.movement[entity] = {
            "origin": origin,
            "destination": destination,
            "time_to_arrival": travel_time,
        }
        self.store_entity_in_transit(entity, origin, destination)


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