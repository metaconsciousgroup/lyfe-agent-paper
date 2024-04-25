import argparse
import logging
from lyfe_agent import get_env_vars, create_agent
from omegaconf import OmegaConf
from pathlib import Path
from expand_brain_config import expand_brain_configuration
from utils.config_utils import parse_config
from utils.saveload import (
    close_agents,
    load_memory_to_cfg,
)
import utils.thread_pool as thread_pool


logger = logging.getLogger(__name__)


def run_interview(interview_question, agent):
    interview_question = "The interviewer says: " + interview_question
    response = agent({"interview": interview_question, "time": "0"})
    return response

def setup_logging():
    logging.basicConfig(level=logging.INFO)  # Configure root logger
    logging.getLogger("lyfe_agent.chains").setLevel(logging.DEBUG)
    logging.getLogger("lyfe_python_env").setLevel(logging.DEBUG)


def main():
    """
    This function conducts an evaluation across multiple runs of a given simulation.

    For each run, it loads the data of agents involved, and performs evaluations as specified in the configuration (cfg).
    It maintains evaluation dictionaries 'eval_multirun_agents_dict' and 'eval_multirun_logs_dict' to track performance across all runs.
    Some metrics are only calculated for run-specific evaluations, and are not tracked across runs.

    Arguments:
    - cfg: Configuration object that contains paths, evaluation criteria, and other settings.
    """

    ### SET UP BEFORE EVALUATION ###
    setup_logging()
    parser = argparse.ArgumentParser(description="Evaluate agents with memory config.")
    parser.add_argument(
        "--config_path",
        type=str,
        help="Path to the directory containing the agents' base configuration.",
        required=True,
    )
    parser.add_argument(
        "--agent_memory_dir",
        type=str,
        help="Path to the directory containing the agents' memory.",
        required=True,
    )
    parser.add_argument(
        "--agent_name",
        type=str,
        help="Name of the agent to be interviewed.",
        required=True,
    )

    parser.add_argument(
        "--interview_question",
        type=str,
        help="Question to ask the agent.",
        required=True,
    )

    args = parser.parse_args()

    agent_cfg_dict = None

    # load original agent config
    agent_cfg_path = Path(args.config_path)
    agent_memory_dir = Path(args.agent_memory_dir)
    if agent_cfg_path.exists() and agent_memory_dir.exists():
        logger.info(f"Loading agent config from {agent_cfg_path}")
        agent_cfg = OmegaConf.load(agent_cfg_path)
        agent_cfg = expand_brain_configuration(agent_cfg)
        parse_config(agent_cfg)
        logger.info(f"Loading agent memory from {agent_memory_dir}")
        load_memory_to_cfg(agent_cfg.agents, agent_memory_dir)
        agent_cfg_dict = agent_cfg.agents.dict
    else:
        raise AssertionError("No agent config found.")
    
    # TODO: this should not be hardcoded
    base_dir = Path(__file__).resolve().parent
    anim_embedding_path = base_dir / "database" / "anim_embeddings.json"

    (agent_id, agent_cfg) = _get_agent_cfg_by_name(agent_cfg_dict, args.agent_name)
    executor = thread_pool.start_executor()

    env_dict = get_env_vars(env_file_path=".env", anim_embedding_path=anim_embedding_path)

    agent = create_agent(agent_cfg=agent_cfg, agent_id=agent_id, executor=executor, env_dict=env_dict, wait_until_ready=True)


    response = run_interview(args.interview_question, agent)["interview"]
    second_question = "Are there any questions you have for me?"
    next_response = run_interview(second_question, agent)["interview"]
    logger.info(f"Question {args.interview_question}")
    logger.info(f"Response {response}")
    logger.info(f"Question {second_question}")
    logger.info(f"Next response {next_response}")

    close_agents([agent])

    return response


def _get_agent_cfg_by_name(agent_cfg_dict, name):
    for agent_id, agent_cfg in agent_cfg_dict.items():
        if agent_cfg.first_name + " " + agent_cfg.last_name == name:
            return (agent_id, agent_cfg)
        elif hasattr(agent_cfg, "name") and agent_cfg.name == name:
            return (agent_id, agent_cfg)
    raise ValueError(f"Could not find agent with name {name}")


if __name__ == "__main__":
    main()
