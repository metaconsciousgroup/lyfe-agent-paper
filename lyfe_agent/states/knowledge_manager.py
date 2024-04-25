import logging
import random
import copy
import numpy as np
from omegaconf import OmegaConf
from scipy.spatial.distance import cdist

from lyfe_agent.brain_utils import RewardModel
from lyfe_agent.base import BaseState

logger = logging.getLogger(__name__)
class KnowledgeManager(BaseState):
    def __init__(self, brain_cfg, agent_cfg):
        self.brain_cfg = brain_cfg

        self.reward_model = self.setup_reward_model(
            model_type=self.brain_cfg.reward_model_type,
            embedding_model=self.brain_cfg.word_embedding_model,
        )

        self.bag_knowledge = copy.deepcopy(
            OmegaConf.to_container(self.brain_cfg.get("inventory", {}))
        )

        self.preference_knowledge = copy.deepcopy(
            OmegaConf.to_container(self.brain_cfg.get("preference", {}))
        )

        self.preference_embedding = self.setup_preference_embedding()

        self.map = {}
        self.set_map(agent_cfg.get("map", []))

    def set_map(self, map):
        # Convert the map list to a dictionary with empty strings as values
        self.map = {location: "" for location in map}

    def update(self, observations):
        # Update the map with new locations from observations
        for location in observations.get("locations", []):
            if location not in self.map:
                logger.info(f"Adding location {location} to the map.")
            self.map[location] = ""  # Add location with an empty string as its value

    def get_map_content(self, location):
        if not self.map:
            return "None"

        # To remove the current location in the map for choosing the next destination
        updated_map = [
            name
            for name in self.map
            if not (location.arrival and name == location.destination)
        ]
        return ", ".join([name.replace("_", " ") for name in updated_map])

    def setup_reward_model(self, model_type="arg_max", embedding_model="none"):
        model_type_dict = {
            "arg_max": "ArgMaxModel",
            "neural_network": "NeuralNetworkModel",
            "transformer": "TransformerModel",
        }

        if model_type not in model_type_dict.keys():
            raise ValueError(f"Model type {model_type} not supported.")

        embedding_model = None if embedding_model == "none" else embedding_model
        return RewardModel(self.brain_cfg, model_type_dict[model_type], embedding_model)

    def setup_preference_embedding(self):
        if self.reward_model.embedding_model is None:
            self.preference_embedding = None
            return

        self.preference_embedding = {}
        for domain, items in self.bag_knowledge.items():
            self.preference_embedding[domain] = {}
            for item in items.keys():
                if item in self.preference_knowledge.get(domain, {}):
                    self.preference_embedding[domain][
                        item
                    ] = self.reward_model.add_knowledge(item)

    def get_knowledge(self, item, domain=None):
        if self.reward_model.embedding_model is None:
            if domain is not None:
                self.preference_knowledge[domain].setdefault(
                    item, random.randint(1, 10)
                )
            return np.zeros(1)

        item_embedding = self.reward_model.add_knowledge(item)
        domains_to_search = [domain] if domain else self.preference_embedding.keys()
        embeddings = np.concatenate(
            [list(self.preference_embedding[d].values()) for d in domains_to_search]
        )
        all_keys = sum(
            [list(self.preference_embedding[d].keys()) for d in domains_to_search], []
        )

        sim_matrix = 1 - cdist(item_embedding[np.newaxis], embeddings, metric="cosine")
        sim_max_index = np.argmax(sim_matrix)
        max_sim, max_sim_item = sim_matrix[0][sim_max_index], all_keys[sim_max_index]
        max_sim_domain = domain or self._get_domain(max_sim_item)

        if max_sim_domain is not None:
            magnify_factor = 1.5
            self.preference_knowledge[max_sim_domain][item] = round(
                max_sim
                * self.preference_knowledge[max_sim_domain][max_sim_item]
                * magnify_factor,
                2,
            )
            self.preference_embedding[max_sim_domain][item] = item_embedding

    def _get_domain(self, item):
        return next(
            (d for d, items in self.preference_embedding.items() if item in items), None
        )

    def get_bag_content(self):
        contents = [
            f"{item.replace('_', ' ')}: {number}"
            for domain in self.bag_knowledge
            for item, number in self.bag_knowledge[domain].items()
        ]
        return ", ".join(contents)

    def preferred_item(self, domain=None, observation=None):
        """
        Get the action based on the model type
        domain: domain of the action (e.g. food, utils)
        observation: observation that is used in model-free RL, but in Agent, we can always get access to the observation(i.e. the bag and preference)
        """
        if self.reward_model.reward_method == "ArgMaxModel":
            return self.reward_model._get_arg_max_action(domain, observation)
        elif self.reward_model.reward_method == "NeuralNetworkModel":
            return self.reward_model._get_neural_network_action(domain, observation)
        elif self.reward_model.reward_method == "Transformer":
            return self.reward_model._get_transformer_action(domain, observation)
        else:
            raise ValueError(f"Unknown model type: {self.reward_model.reward_method}")
