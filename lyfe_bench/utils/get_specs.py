import json
import os

from typing import Dict, Tuple

# Get the directory of the current module
module_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "benchmarks")

# SafeDict used for string formatting: `str.format()` cannot deal with missing keys, so this is our workaround
class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

def get_unprocessed_specs(path: str) -> Tuple[Dict]:
    """
    Get the specs from a json file.
    Input: path to json file in lyfe_bench module
    Output: pair of dictionaries with specifications
    """
    if not path.endswith(".json"):
        path += ".json"
    scenarios_dir = os.path.join(module_dir, "scenarios")
    benchmark_path = os.path.join(scenarios_dir, path)

    with open(benchmark_path, "r") as f:
        benchmark_specs = json.load(f)

    # depends on position of agents specs
    agents_path = os.path.join(module_dir, "agents/agents.json")

    with open(agents_path, "r") as f:
        agents_specs = json.load(f)

    return benchmark_specs, agents_specs

def process_judge_interview(eval_item: Dict, tag_to_name: Dict[str, str]):
    """
    Process a judge_interview item. By replacing templates with agent names.
    """
    eval_item["question"] = eval_item["question"].format_map(tag_to_name)
    eval_item["answer"] = eval_item["answer"].format_map(tag_to_name)

def process_extract_interview(eval_item: Dict, tag_to_name: Dict[str, str]):
    """
    Process an extract_interview item. By replacing templates with agent names.
    """
    eval_item["question"] = eval_item["question"].format_map(tag_to_name)
    eval_item["template"] = eval_item["template"].format_map(tag_to_name)
    for key in eval_item["format"].keys():
        eval_item["format"][key] = eval_item["format"][key].format_map(tag_to_name)

def process_agents_specs(specs: Dict, agents: Dict):
    """
    Process the benchmark specs to get the kwargs for the testbed environment.
    """
    agent_id_mapping = {agent["id"]: agent for agent in agents}
    agent_specs = specs["agents"]
    tag_to_name = SafeDict({tag: agent_id_mapping[data["default_id"]]["name"] for tag, data in agent_specs.items()})

    # add agent details to specs
    for agent_data in agent_specs.values():
        agent_id = agent_data["default_id"]
        del agent_data["default_id"]

        # process information to include agent names where tags are previously present
        new_agent_data = agent_id_mapping[agent_id]
        if "goal" in agent_data.keys():
            new_agent_data["goal"] = agent_data["goal"].format_map(tag_to_name)
        if "task_relevant_memories" in agent_data.keys():
            new_agent_data["task_relevant_memories"] = [mem.format_map(tag_to_name) for mem in agent_data["task_relevant_memories"]]
        if "task_irrelevant_memories" in agent_data.keys():
            new_agent_data["task_irrelevant_memories"] = [mem.format_map(tag_to_name) for mem in agent_data["task_irrelevant_memories"]]

        agent_data.update(new_agent_data)

        # augment memory
        task_rel_mem = agent_data.pop("task_relevant_memories", [])
        task_irrel_mem = agent_data.pop("task_irrelevant_memories", [])
        agent_data["memory"] += task_rel_mem + task_irrel_mem

    # further process information in evaluation to include agent names where tags are previously present
    eval_specs = specs["evaluation"]
    for eval_item in eval_specs:
        if eval_item["method"] == "judge_interview":
            process_judge_interview(eval_item, tag_to_name)
        elif eval_item["method"] == "extract_interview":
            process_extract_interview(eval_item, tag_to_name)

def get_specs(path: str) -> Dict:
    """
    Get processed specs from a json file.
    Input: path to json file in lyfe_bench module
    Output: tuple of
    """
    benchmark_specs, agents_specs = get_unprocessed_specs(path)
    process_agents_specs(benchmark_specs, agents_specs)
    return benchmark_specs