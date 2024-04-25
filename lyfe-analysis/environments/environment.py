import logging

from lyfe_python_env import LyfeWebsocketWrapper

from environments.migration_utils import construct_unity_scene


logger = logging.getLogger(__name__)


def get_environment(cfg, agents_dict=None, env_dict=None, evaluators_dict=None, save_dir=None):
    cfg_env = cfg.environment
    cfg_agents = cfg.agents
    logger.info(f"[SYSTEM][SETUP ENVIRONMENT TYPE] {cfg_env.type}")
    # logger.info(f"[SYSTEM][SETUP FRAME RATE] {cfg_env.frame_rate}")

    if cfg_env.type == "unity":
        return load_unity_env(cfg_env, cfg_agents, env_dict)
    elif cfg_env.type in ["benchmark", "target"]:
        return load_target_env(cfg_env, cfg_agents,agents_dict, evaluators_dict, save_dir=save_dir)
    else:
        raise ValueError(f"Unknown environment type")


def load_target_env(cfg_env, cfg_agents, agents_dict, evaluators_dict, save_dir=None):
    from hydra.utils import instantiate

    logger.info(f"[SYSTEM] Loading target environment.")
    env = instantiate(cfg_env)(agents_dict=agents_dict, evaluators_dict=evaluators_dict, save_dir=save_dir)
    return env


def load_unity_env(cfg_env, cfg_agents, env_dict):
    from lyfe_agent import ExternalEnvWrapper

    logger.info(f"[SYSTEM] Loading Unity environment.")
    unity_scene = construct_unity_scene(cfg_agents)

    external_websocket_server = cfg_env.get("external_websocket_server", False)
    communicator_url = cfg_env.get("communicator_url", "localhost")
    simulation_id = cfg_env.get("simulation_id", None)
    enable_monitoring = cfg_env.get("enable_monitoring", False)
    logger.info(
        f"[SYSTEM] external_websocket_server: {external_websocket_server} communicator_url: {communicator_url} simulation_id: {simulation_id} enable_monitoring: {enable_monitoring}"
    )
    try:
        websocket_env = LyfeWebsocketWrapper(
            out_data_scene=unity_scene,
            enable_client_auth=False,
            enable_monitoring=enable_monitoring,
            external_websocket_server=external_websocket_server,
            websocket_url=communicator_url,
            simulation_id=simulation_id,
        )
    except BaseException as e:
        logger.error(f"[SYSTEM] Error loading Unity environment: {e}")
        raise e
    logger.info(f"[SYSTEM] Successfully loaded Unity environment.")

    agent_names = [cfg_agent.name for cfg_agent in cfg_agents["dict"].values()]
    # need to make sure agent ID to name mappings are consistent
    unity_resource = websocket_env.get_unity_resources()
    id_name_mapping = [
        unity_resource.get_agent(id).user.username
        for id in unity_resource.get_agent_id_list()
    ]
    assert agent_names == id_name_mapping, "inconsistent agent ordering"

    logger.info(f"[SYSTEM] Wrapping Unity environment.")
    try:
        env = ExternalEnvWrapper(
            websocket_env,
            agent_names=agent_names,
            frame_rate=cfg_env.frame_rate,
            sim_speed=cfg_env.sim_speed,
            world_time=cfg_env.world_time,
            enable_monitoring=enable_monitoring,
            env_dict=env_dict,
        )
    except BaseException as e:
        logger.error(f"[SYSTEM] Error wrapping Unity environment: {e}")
        raise e
    logger.info(f"[SYSTEM] Successfully initialized Unity environment.")

    return env
