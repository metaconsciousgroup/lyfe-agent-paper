from concurrent.futures import Executor
import logging
import os
import signal
import traceback

from omegaconf import DictConfig

from lyfe_agent import create_agents, EncoderManager, EncoderCollection, OpenAIEncoder
from environments import get_environment

import utils.thread_pool as thread_pool
from utils.saveload import store_agent_memory, close_agents

logger = logging.getLogger(__name__)


class TerminationSignal(Exception):
    pass


def sigterm_handler(signum, frame):
    raise TerminationSignal("Received SIGTERM signal.")


signal.signal(signal.SIGTERM, sigterm_handler)


def run_agents(cfg: DictConfig, env_dict: dict[str, str]):
    """The key loop for running agents in environments."""

    logger.info("\n\n[SYSTEM] Entering run_agents function...")
    executor: Executor = thread_pool.start_executor()
    cfg_env = cfg.environment
    enable_monitoring = cfg_env.get("enable_monitoring", False)
    checkpoint = cfg.general.checkpoint
    collect_data = cfg.general.collect_data
    save_dir = os.getcwd()
    # Get a list of all agents
    encoder = _create_encoder(executor, env_dict)
    agents_dict = create_agents(
        cfg.agents.dict,
        env_dict=env_dict,
        wait_until_ready=False,
        encoder=encoder,
        executor=executor,
    )
    agents = list(agents_dict.values())

    if cfg_env.get("type", "unity") == "benchmark":
        from evaluation.eval_utils import create_evaluators

        evaluators_dict = create_evaluators(cfg.get("evaluators"))
        env = get_environment(
            cfg,
            agents_dict=agents_dict,
            env_dict=env_dict,
            evaluators_dict=evaluators_dict,
            save_dir=save_dir,
        )
    else:
        env = get_environment(cfg, agents_dict=agents_dict, env_dict=env_dict)
    env.wait_until_ready(timeout=300)

    # TODO: For simulations that needs to adjust with the number of agents
    cfg.general.max_iter = max(
        len(agents) * cfg.general.max_iter_per_agent, cfg.general.max_iter
    )

    max_steps = cfg.general.max_iter
    done = False
    i = 0
    try:
        while i < max_steps and not done:
            for agent_index in range(len(agents)):
                # Get current agent
                agent = agents[agent_index]

                # Get observation, etc. for current agent
                observations = env.get_observations(agent_index)

                # Generate action given current observations and history
                action = agent(observations)

                env.set_action(agent_index, action)

                i += 1
                # Enable storing agent memory periodically when running on server.
                if i % checkpoint == 0 and collect_data:
                    logger.info(
                        f"[SYSTEM] Storing agent memory at step {i} (checkpoint={checkpoint})"
                    )
                    store_agent_memory(
                        agents, path=save_dir, checkpoint=i, is_last=False
                    )

            done = env.time_update()

    except KeyboardInterrupt:
        logger.info(f"[SYSTEM] Interrupted by user at step {i}. Shutting down...")
    except TerminationSignal:
        logger.info(f"[SYSTEM] Received SIGTERM signal at step {i}. Shutting down...")
    except Exception as e:
        traceback_string = traceback.format_exc()
        logger.warning(f"[SYSTEM] Exception occurred at step {i}: {traceback_string}")
    finally:
        # Always perform clean-up, regardless of whether an exception occurred
        logger.info(
            f"[SYSTEM] Cleaning up after {i} steps (with max_steps={max_steps}). This may take a while..."
        )
        if enable_monitoring:
            env.plot_timings()
        env.close()
        store_agent_memory(agents, path=save_dir, is_last=True)
        close_agents(agents)

    logger.info("[SYSTEM] Exiting run_agents function...\n\n")


# Find a better place to instantiate encoder manager
def _create_encoder(executor: Executor, env_dict: dict[str, str]):
    """
    Create an encoder for a list of agents.
    """
    logger.info("[SYSTEM] Creating new encoder...")
    openai_encoder_manager = EncoderManager(
        encoder_func=OpenAIEncoder(model_name="text-embedding-3-small"),
        batch_size=50,
        max_wait_time=0.5,
        env_dict=env_dict,
        executor=executor,
    )
    # Why does encoder_model.run() need to be called here?
    openai_encoder_manager.run()
    encoder_collection = EncoderCollection(
        models={"openai": openai_encoder_manager},
        rules={"recentmem": "openai", "longmem": "openai", "obsbuffer": "openai"},
        validation_config=["recentmem", "longmem", "obsbuffer"],
    )
    return encoder_collection
