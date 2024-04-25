import hydra
import os
import json
import time
import pickle
from agent import get_agents
from agent.langmodel import get_api_keys
from omegaconf import OmegaConf
from pathlib import Path
from typing import List, Dict, Any
from expand_brain_config import expand_brain_configuration
from utils.config_utils import parse_config
from utils.saveload import (
    close_agents,
    load_agent_memory,
    load_memory_to_cfg,
    _wait_for_memory_embedding,
)
import utils.thread_pool as thread_pool

from langchain.chat_models import ChatOpenAI

from settings import BASE_DIR


def eval_multirun_agents(cfg, agents, eval_dict) -> Dict[str, Any]:
    """Given an interview config, list of agents, and evaluation dictionary, interview agents and update evaluation dictionary."""
    api_key = get_api_keys()["openai"][0]
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key)
    base_kwargs = {"llm": llm}
    for name, agent in agents.items():
        base_kwargs["agent"] = agent
        for topic, interview_content in cfg[name].items():
            kwargs = {"results_dict": eval_dict[name][topic]} | base_kwargs.copy()
            eval_func = hydra.utils.instantiate(interview_content)
            eval_dict[name][topic] = eval_func(**kwargs)
    return eval_dict


def eval_multirun_logs(cfg, cwdir, eval_dict) -> Dict[str, Any]:
    """Given a log and evaluation dictionary, analyze interactions and update evaluation dictionary."""
    api_key = get_api_keys()["openai"][0]
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=api_key)

    for mention, content in cfg.items():
        kwargs = {"cwdir": cwdir, "results_dict": eval_dict[mention], "llm": llm}
        eval_func = hydra.utils.instantiate(content)
        eval_dict[mention] = eval_func(**kwargs)
    return eval_dict


def eval_run(cfg, cwdir):
    """Given a configuration and a directory, evaluate each run and generate plots according to to function called"""
    for func, content in cfg.items():
        kwargs = {"path": cwdir}
        eval_func = hydra.utils.instantiate(content)
        eval_func(**kwargs)
        print(f"Finished {func} evaluation.")


def select_run():
    base_dir = "multirun"
    dates = sorted(
        [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    )

    print("Select a date:")
    for i, date in enumerate(dates):
        print(f"{i+1}: {date}")

    date_idx = int(input("Enter the number of the date: ")) - 1
    selected_date = dates[date_idx]

    runs_dir = os.path.join(base_dir, selected_date)
    runs = sorted(
        [d for d in os.listdir(runs_dir) if os.path.isdir(os.path.join(runs_dir, d))]
    )

    print("Select a run:")
    for i, run in enumerate(runs):
        print(f"{i+1}: {run}")

    run_idx = int(input("Enter the number of the run: ")) - 1
    selected_run = runs[run_idx]

    return os.path.join(base_dir, selected_date, selected_run)


@hydra.main(
    version_base=None, config_path="configs/evaluation", config_name="murder_eval"
)
def main(cfg):
    """
    This function conducts an evaluation across multiple runs of a given simulation.

    For each run, it loads the data of agents involved, and performs evaluations as specified in the configuration (cfg).
    It maintains evaluation dictionaries 'eval_multirun_agents_dict' and 'eval_multirun_logs_dict' to track performance across all runs.
    Some metrics are only calculated for run-specific evaluations, and are not tracked across runs.

    Arguments:
    - cfg: Configuration object that contains paths, evaluation criteria, and other settings.
    """

    ### SET UP BEFORE EVALUATION ###

    if cfg.get("reset_path", None):
        cfg.path = select_run()
        print(f"Selected run: {cfg.path}")

    dir = Path(cfg.path)


    for repetitions in range (3):

        if cfg.get("post_process", None):
            if not os.path.isfile(dir / "0/main_log.csv"):
                eval_func = hydra.utils.instantiate(cfg.post_process)
                eval_func(dir)
        else:
            print(
                "Warning: No post-processing function specified. Many metrics are dependent on post-processing."
            )

        run_num = 0
        # setup evaluation dictionary
        if cfg.get("eval_multirun_agents", None):
            eval_multirun_agents_dict = {
                name: {topic: {} for topic in cfg.eval_multirun_agents[name]}
                for name in cfg.eval_multirun_agents.keys()
            }
        # get log data here
        if cfg.get("eval_multirun_logs", None):
            eval_multirun_logs_dict = {
                mention: {} for mention in cfg.eval_multirun_logs.keys()
            }

        if cfg.get("eval_convergence", None):
            eval_convergence_dict = {
                memory_component: {}
                for memory_component in original_agents_data[0].memory.memory_keys
            }

        ### EVALUATION START ###

        while os.path.exists(Path(dir / str(run_num))):
            cwdir = Path(dir / str(run_num))
            run_num += 1

            # multi-run evaluations
            if cfg.get("eval_multirun_agents", None):
                # load original agent config
                agent_cfg_path = Path(dir / "0/.hydra/config.yaml")
                if agent_cfg_path.exists():
                    agent_cfg = OmegaConf.load(agent_cfg_path)
                    agent_cfg = expand_brain_configuration(agent_cfg)
                    parse_config(agent_cfg)
                    load_memory_to_cfg(agent_cfg.agents, cwdir)
                    executor = thread_pool.start_executor()

                    # # TODO: a hacky way to make it faster
                    # agent_cfg.brain.encoder.models.openai.batch_size = 2000

                    agents_data = get_agents(agent_cfg, executor=executor)

                    agents = {
                        agent.name: agent
                        for agent in agents_data
                        if agent.name in cfg.eval_multirun_agents
                    }

                    # make sure that agent's memory has been loaded, otherwise prompt for first several agents will not contain memory
                    _wait_for_memory_embedding(agents_data, agent_cfg.agents.dict)

                    print("LOADMEM")

                else:
                    AssertionError("No agent config found.")

                eval_multirun_agents_dict = eval_multirun_agents(
                    cfg.eval_multirun_agents, agents, eval_multirun_agents_dict
                )
                # thread_pool.shutdown_executor(executor)
                close_agents(agents_data)

            if cfg.get("eval_multirun_logs", None):
                eval_multirun_logs_dict = eval_multirun_logs(
                    cfg.eval_multirun_logs, cwdir, eval_multirun_logs_dict
                )

            # per-run evaluations
            if cfg.get("eval_run", None):
                eval_run(cfg.eval_run, cwdir)

            if cfg.get("eval_convergence", None):
                agent_memories = load_agent_memory(cwdir, type="json")
                agent_memories = agent_memories[cfg.eval_convergence.agent]
                for memory_component in eval_convergence_dict.keys():
                    memories_to_save = agent_memories[memory_component]
                    eval_convergence_dict[memory_component][run_num - 1] = memories_to_save

        # save evaluation dictionary
        if cfg.get("eval_multirun_agents", None):
            print(eval_multirun_agents_dict)
            if os.path.exists(dir):
                with open(Path(dir / f"eval_multirun_agents_{repetitions}.pkl"), "wb") as f:
                    pickle.dump(eval_multirun_agents_dict, f)  # get log data here
        if cfg.get("eval_multirun_logs", None):
            print(eval_multirun_logs_dict)
            if os.path.exists(dir):
                with open(Path(dir / "eval_multirun_logs.pkl"), "wb") as f:
                    pickle.dump(eval_multirun_logs_dict, f)

        if cfg.get("eval_convergence", None):
            with open(Path(dir / "output.json"), "w") as json_file:
                json.dump(eval_convergence_dict, json_file, indent=4)


if __name__ == "__main__":
    main()
