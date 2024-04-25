"""Functions for incepting new memories in agents.

This is mainly for testing the impact of injecting memory content in agents.
"""

import random
from omegaconf import ListConfig
from lyfe_agent.utils.name_utils import name_higher2lower


def inception(env, env_type, agents, cfg):
    if env_type == "unity":
        env_agents = [
            agent
            for agent in agents
            if agent.name in env.get_agent_names()
        ]
    else:
        env = env.unwrapped
        env_agents = [agent for agent in agents if agent.name in env.agents]

    inception_types = [inception_type for inception_type in cfg]

    names = [name_higher2lower(agent.name) for agent in env_agents]
    inception_data = {
        inception_type: {name: cfg[inception_type].get("all", "") for name in names}
        for inception_type in inception_types
    }

    for inception_type in inception_types:
        groups = inception_data[inception_type]
        for key, sub_cfg in cfg[inception_type].items():
            # when `key` corresponds to a single agent (`sub_cfg` is the message string)
            if isinstance(sub_cfg, str):
                if key in groups:
                    groups[key] += " " + sub_cfg
                continue
            elif "members" not in sub_cfg:
                continue

            members = sub_cfg.members
            # the case where the group is prespecified
            if isinstance(members, ListConfig):
                for member in members:
                    groups[member] += " " + sub_cfg.message
            # the case where the group is random
            elif "random" in members:
                assert isinstance(
                    sub_cfg.number, int
                ), "Please specify the number of sampled agents."
                group = random.sample(names, sub_cfg.number)
                for member in group:
                    groups[member] += " " + sub_cfg.message

    for agent in env_agents:
        if "observation" in cfg:
            message = inception_data["observation"][name_higher2lower(agent.name)]
            if message != "":
                env.dones[agent.name] = False  ####
                message_sender = ""  # "Myself"
                env.message_system.send_message(message_sender, agent.name, message)

        if "workmem" in cfg:
            workmem = inception_data["workmem"][name_higher2lower(agent.name)]
            agent.memory.add(content=workmem)
