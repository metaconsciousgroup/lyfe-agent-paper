from pathlib import Path
import json
import time
import pickle
import logging
import os

import utils.thread_pool as thread_pool

from lyfe_agent import Agent
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def close_agents(agents):
    """
    Close all threads and processes associated with the agents.
    """
    for agent in agents:
        for mem_key in agent.memory.memory_keys:
            mem_module = getattr(agent.memory, mem_key)
            if getattr(mem_module, "encoder", None):
                mem_module.encoder.stop()
        executor = agent.executor
    thread_pool.shutdown_executor(executor)


def store_agent_memory(agents, path=None, is_last=True, checkpoint=None):
    """
    Store agent memory into a json file
    Stored things: name, working memory, recent memory, longterm memory, contact, map, bag_knowledge, preference_knowledge
    """
    # TODO: This should be moved somewhere else
    if path is None:
        path = os.getcwd()
    agents_content = dict()

    # Aggregate all agent data
    data_collectors = {}

    for agent in agents:
        # Summarize the last set of memories into higher order memories
        agent.memory.update(
            # is_last=is_last, no_summary=agent.brain_cfg.get("no_summary", False)
            is_last=is_last,
        )

        agent_content = {
            "name": agent.name,
            "contacts": agent.contacts.get_contacts(),
            "bag": agent.knowledge.bag_knowledge,
            "preference": agent.knowledge.preference_knowledge,
            # "token_monitor": agent.inner_status.token_monitor.info,
            # "inner_status": agent.inner_status.info,
            "map": agent.knowledge.map,
        }
        # # custom knowledge about particular agent
        # for key, value in agent.innate.items():
        #     agent_content[key] = value
        # memory content for each memory key
        for mem_key in agent.memory.memory_keys:
            mem_module = getattr(agent.memory, mem_key)
            agent_content[mem_key] = mem_module.items if mem_module else None
        agents_content[agent.name] = agent_content

        # Collect data from lyfe_agent (may want to separate the different data)
        for key, value in agent.data_collectors.items():
            if key not in data_collectors:
                data_collectors[key] = []

            # TODO: HACK: TEMP for memory_input_collector, need to change to a general way for agent-based collector
            if key == "memory_input_collector":
                data_collectors[key].append({agent.name: value})
            else:
                data_collectors[key].extend(value)

    # save to a json file
    savePath = Path(path) / "agent_memory.json" if checkpoint is None else Path(path) /f"ckpts/{checkpoint}/agent_memory.json"
    savePath.parent.mkdir(parents=True, exist_ok=True)
    with open(savePath, "w") as f:
        logger.info(f"[SYSTEM] Storing {len(agents)} agents memory...")
        json.dump(agents_content, f, indent=4)

    # if agents[0].test_mode:
    #     # save to a pickle file
    #     savePath_pickle = Path(path) / "agent_memory.pkl"
    #     with open(savePath_pickle, "wb") as f:
    #         pickle.dump(agents, f)

    if data_collectors:
        for key, data_collector in data_collectors.items():
            # TODO: TEMP for memory_input_collector
            if key == "memory_input_collector":
                # save to a json file
                savePath = Path(path) / f"{key}.json" if checkpoint is None else Path(path) /f"ckpts/{checkpoint}/{key}.json"
                savePath.parent.mkdir(parents=True, exist_ok=True)
                with open(savePath, "w") as f:
                    json.dump(data_collector, f, indent=4)
            else:
                # save to a json file
                savePath = Path(path) / f"{key}_chain_data.json"
                with open(savePath, "w") as f:
                    json.dump(data_collector, f, indent=4)


def load_agent_memory(path, type):
    """Load agent memory from a file."""
    # TODO: This should be moved somewhere else
    if type == "json":
        loadPath = Path(path) / "agent_memory.json"
        with open(loadPath, "rb") as f:
            agents = json.load(f)
    elif type == "pickle" or type == "pkl":
        loadPath = Path(path) / "agent_memory.pkl"
        with open(loadPath, "rb") as f:
            agents = pickle.load(f)
    return agents


def load_memory_to_cfg(cfg, path):
    """Load agent memory from a json and write to agent cfg."""
    json_data = load_agent_memory(path, type="json")
    for agent_cfg in cfg.dict.values():
        for memory_type in agent_cfg.memory.keys():
            agent_name = agent_cfg.name
            if memory_type in json_data[agent_name]:
                agent_cfg.memory[memory_type] = json_data[agent_name][memory_type]
    return agent_cfg


@DeprecationWarning
def load_agent_data(cwdir: str, agents_data: List[Agent]) -> Dict[str, Any]:
    """Load agent data from directory to an existing list of agent data."""
    # Modify agents with their information after a specific run
    json_data = load_agent_memory(cwdir, type="json")
    for agent_name, agent in agents_data.items():
        data = json_data[agent_name]

        for memory_component in agent.memory.memory_keys:
            if memory_component in data:
                memory = getattr(agent.memory, memory_component)
                memory.clear()
                for i in data[memory_component]:
                    memory.add(i)
            else:
                print(f"Warning: {agent.name} does not have memory {memory}")

    return agents_data


def load_chain_data(config_path):
    """
    Load and restructure the chain data.

    Parameters:
        config_path (str): The path to the configuration file.

    Returns:
        dict: The restructured chain data.
    """

    # Load chain data
    with open(config_path) as f:
        llm_response_data = json.load(f)

    # Restructure the data by active_func
    chain_data = {}
    for entry in llm_response_data:
        active_func_value = entry["input"]["active_func"]
        if active_func_value not in chain_data:
            chain_data[active_func_value] = []
        chain_data[active_func_value].append(entry)

    return chain_data
