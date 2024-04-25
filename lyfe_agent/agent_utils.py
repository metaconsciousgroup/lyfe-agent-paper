"""Utilities for agents."""
from concurrent.futures import Executor
import logging
from lyfe_agent.agent import Agent
import time
from lyfe_agent.utils.encoder_utils import EncoderCollection

logger = logging.getLogger(__name__)


def create_agents(
    agent_config_dict,
    encoder: EncoderCollection,
    executor: Executor,
    env_dict: dict[str, str],
    wait_until_ready: bool = False,
) -> dict[str, Agent]:
    """
    Create a list of agents from the config file.
    :agent_config_dict: Hydra config file
    :executor: Executor for the encoder manager of this agent.
    """
    logger.info(f"[SYSTEM] Number of agents from config: {len(agent_config_dict)}")

    agents = dict()
    for agent_id, agent_config in agent_config_dict.items():
        agent = create_agent(
            agent_config,
            agent_id,
            encoder=encoder,
            executor=executor,
            env_dict=env_dict,
            wait_until_ready=False,
        )
        agents[agent_id] = agent

    if wait_until_ready:
        # TODO: Figure out why memory embedding takes so long
        logger.info(
            f"[SYSTEM] Waiting for memory embedding for {len(agents)} agents..."
        )
        for agent in agents:
            _wait_for_memory_embedding_by_config(agent_config_dict[agent.id], agent)

    return agents


def create_agent(
    agent_cfg,  # This is a single agent's config
    agent_id: str,
    env_dict: dict[str, str] = None,
    encoder : EncoderCollection = None,
    executor: Executor = None,
    wait_until_ready: bool = False,
) -> Agent:
    """
    :agent_cfg: Configuration for a single agent
    :agent_id: ID of the agent
    :executor: Executor for the encoder manager of this agent.
    :encoder: Encoder for the agent. If None, create a new one.

    If there is an encoder passed in, then the executor is ignored.
    """

    logger.info("[SYSTEM] Creating new agent...")

    if encoder is None:
        raise ValueError("Encoder cannot be None.")

    try:
        brain_cfg = agent_cfg.brain  # New setup with agent-specific brain
        agent = Agent(
            agent_id,
            agent_cfg=agent_cfg,
            brain_cfg=brain_cfg,
            encoders=encoder,
            executor=executor,
            memory_bank=[],
            env_dict=env_dict,
        )
    except Exception as e:
        import traceback

        stack_trace = traceback.format_exc()
        logger.error(
            f"[SYSTEM] Error initializing agent: {e}\nStack Trace:\n{stack_trace}\nagent_cfg: {agent_cfg}"
        )
        raise e

    if wait_until_ready:
        _wait_for_memory_embedding_by_config(agent_cfg, agent)

    logger.info(f"[SYSTEM] Initialized agent ID {agent.id}, Name {agent.name}")
    return agent


def _wait_for_memory_embedding_by_config(agent_cfg, agent) -> None:
    """Wait for the specific agent's memory to be embedded."""
    agent_memory_length = len(agent_cfg["memory"]["longmem"])
    logger.info(
        f"[SYSTEM] Waiting for memory embedding for {agent.name} length {agent_memory_length}..."
    )
    start = time.time()
    while len(agent.memory.longmem.memory_bank) <= 0:
        # the embedding is still processing
        time.sleep(1)
        if time.time() - start > 60:
            logger.warning(
                f"Waited for 60 seconds but the memory embedding is still not done"
            )
            break
    logger.info(
        f"[SYSTEM] Memory embedding for {agent.name} has length {len(agent.memory.longmem.memory_bank)} from {agent_memory_length} documents."
    )
