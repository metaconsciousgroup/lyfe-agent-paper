import logging
import hydra
from omegaconf import DictConfig, OmegaConf, open_dict

logger = logging.getLogger(__name__)


def expand_config_by_environment(cfg: DictConfig):
    """
    Given a config, preprocesses it for benchmarks.
    Benchmarks are assumed to provide agent information, so we need to create the agents config.
    """
    if cfg.environment.type == "unity":
        return cfg
    if cfg.environment.type == "benchmark":
        # Create a copy of the config to avoid modifying the original
        new_cfg = OmegaConf.create(cfg)

        specs = hydra.utils.instantiate(new_cfg.environment.benchmark_data)

        # Create agents config (TODO: make agent interface more universal)
        agents_dict = {}
        for agent_tag, agent_spec in specs["agents"].items():
            agent_dict = {}
            agent_dict["name"] = agent_spec["name"]
            agent_dict["memory"] = {
                "workmem": ["Nothing"],
                "recentmem": ["Nothing"],
                "convomem": ["Conversation started here"],
                "longmem": agent_spec["memory"],
            }
            agent_dict["initial_goal"] = agent_spec.get("goal", "Just being.")
            agent_dict["personality"] = agent_spec.get("personality", "happy")
            agent_dict["prefab_path"] = agent_spec.get("prefab_path", "https://models.readyplayer.me/64b068e6dd9942dce7fa044c.glb")
            agents_dict[agent_tag] = agent_dict
        specs["agents"]
        agents_cfg = OmegaConf.create({"dict": agents_dict})

        # Create environment config
        env_dict = {}
        env_dict["type"] = "benchmark"
        if specs['env'].get("user", None):
            env_dict["_target_"] = "lyfe_bench.environments.testbed_env.user_env.UserEnv"
        else:   
            env_dict["_target_"] = "lyfe_bench.benchmarks.env.BenchmarkEnv"
        env_dict["_partial_"] = True
        env_dict["specs"] = specs
        env_cfg = OmegaConf.create(env_dict)

        with open_dict(new_cfg):
            new_cfg.agents = agents_cfg
            del new_cfg.environment.benchmark_data
            new_cfg.environment = env_cfg
        return new_cfg


def update_agent_with_env_knowledge(cfg: DictConfig):
    """Update agent with knowledge of the environment."""
    # This assumes all agents have knowledge of the same environment
    if cfg.get("environment", None) is None:
        return
    if cfg.environment.get("map", None) is None:
        logger.info(f"Environment map is not set")
        return
    locations = list(set(cfg.environment.map))
    logger.info(f"Environment map: {locations}")
    with open_dict(cfg):
        # Be more precise with the agent map.
        for agent_cfg in cfg.agents.dict.values():
            agent_cfg.map = locations


def parse_config(cfg: DictConfig):
    """In place parsing of the config."""
    if cfg.environment.type == "unity":
        # Set agents to have knowledge of the environments
        update_agent_with_env_knowledge(cfg)


def expand_brain_configuration(cfg: DictConfig):
    """Set default brain configuration for agents that don't have a brain specified."""
    with open_dict(cfg):
        for key, agent_cfg in cfg.agents.dict.items():
            brain_cfg_name: str = agent_cfg.get("brain", None)
            if brain_cfg_name is not None:
                agent_cfg.brain = brain_cfg_name
            else:
                agent_cfg.brain = cfg.brain
    return cfg
