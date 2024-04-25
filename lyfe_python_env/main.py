from copy import deepcopy
import logging
import json
import argparse
from pathlib import Path
import random
from collections import defaultdict
import platform
from enum import Enum
import time
from lyfe_python_env.datatype.unity_player import UnityPlayer

from lyfe_python_env.time_decorator import CodeTimer, plot_timings
from lyfe_python_env.unity_resources import UnityResources
from lyfe_python_env.unity_websocket_wrapper import LyfeWebsocketWrapper

logger = logging.getLogger(__name__)


UNITYBUILDPATH = Path("./Builds")
UNITYFILENAME = "genagentminimal"
MOCKACTIONPATH = Path("./tests/mock_actions/")
GAMEDATAPATH = Path("./tests/game_data/")


class Platform(Enum):
    LINUX = "Linux"
    DARWIN = "Darwin"
    WINDOWS = "Windows"


def get_unity_filename_string(file):
    system_platform = platform.system()
    if system_platform == Platform.LINUX.value:
        FILENAME = UNITYBUILDPATH / "Linux" / (file + ".x86_64")
    elif system_platform == Platform.DARWIN.value:
        FILENAME = UNITYBUILDPATH / "macOS" / (file + ".app")
    elif system_platform == Platform.WINDOWS.value:
        FILENAME = UNITYBUILDPATH / "Windows" / (file + ".exe")
    else:
        raise NotImplementedError(f"Platform {system_platform} not supported")
    if not FILENAME.exists():
        raise FileNotFoundError(
            f"The file {FILENAME} doesn't exist. Check your UNITYBUILDPATH and cfg_env.file."
        )
    return FILENAME


def run_game(
    mock_action=None,
    game_data_file_name=None,
    external_websocket_server=False,
    wait_time_for_ack=60.0,
):
    with open(MOCKACTIONPATH / (mock_action + ".json"), "r") as f:
        mock_action = json.load(f)

    with open(GAMEDATAPATH / (game_data_file_name + ".json"), "r") as f:
        game_data = json.load(f)

    websocket_env_vars = {
        "game_data": game_data,
        "enable_monitoring": True,
        "external_websocket_server": external_websocket_server,
    }
    if external_websocket_server:
        websocket_env_vars["simulation_id"] = "01234"
    websocket_env = LyfeWebsocketWrapper(
        **websocket_env_vars,
    )

    current_time = time.time()
    while websocket_env.get_incoming_message_count() == 0:
        if time.time() - current_time > wait_time_for_ack:
            raise TimeoutError("No incoming messages received")
        time.sleep(0.1)

    global_timings_storage = {}

    def record_timing(name, elapsed_time):
        if name not in global_timings_storage:
            global_timings_storage[name] = []
        global_timings_storage[name].append(elapsed_time)

    # The key loop for running agents in environments.
    logger.info("[SYSTEM] Starting game loop...")
    try:
        i = 0
        max_steps = 1000_000_000
        while i < max_steps:
            for agent_id in websocket_env.get_agent_id_list():
                with CodeTimer(record_timing, "game_loop"):
                    # Get observation, etc. for current agent

                    with CodeTimer(record_timing, "get_observations"):
                        observations = websocket_env.get_observations(agent_id)

                    if observations and not (
                        len(observations) == 1 and "nearby_creature" in observations
                    ):
                        logger.debug(f"{agent_id} Observations: {observations}")

                    # Generate random action
                    if i % 9313 == 0:
                        mock_action_current = replace_player_id(
                            websocket_env.get_unity_resources(), mock_action
                        )
                        random_action = random.choice(mock_action_current)
                        logger.debug(
                            f"{agent_id} Randomly selected action: {random_action}"
                        )
                    else:
                        random_action = defaultdict(lambda: None)

                    # Update environment given action
                    with CodeTimer(record_timing, "update_env"):
                        # env.step(random_action)
                        websocket_env.send_test_action(agent_id, random_action)
                i += 1
            time.sleep(0.005)

    except KeyboardInterrupt:
        logger.info("[SYSTEM] Interrupted by user. Shutting down...")
        # env.plot_timings()
        # plot_timings(global_timings_storage)
        websocket_env.close()


def replace_player_id(unity_resource: UnityResources, mock_actions):
    mock_actions = deepcopy(mock_actions)
    for mock_action in mock_actions:
        # Randomly choose a player
        random_player_id :str = None
        if len(unity_resource.get_player_id_list()) > 0:
            random_player_id = random.choice(unity_resource.get_player_id_list())
        if random_player_id is None:
            continue

        action_dm = mock_action.get("message", None)
        if action_dm is not None:
            _, action_dm_receiver = action_dm
            if action_dm_receiver == "<unity_player_id>":
                mock_action["message"] = [action_dm[0], random_player_id]

        action_look_at = mock_action.get("look_at", None)
        if action_look_at is not None:
            if action_look_at == "<unity_player_id>":
                mock_action["look_at"] = random_player_id
    return mock_actions


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Configure root logger
    parser = argparse.ArgumentParser(description="Run Agents in Environment")
    parser.add_argument(
        "--external_websocket_server",
        action="store_true",
        default=False,
        help="Enable the external websocket server",
    )
    parser.add_argument(
        "--mock", type=str, default="talkmove", help="Mock action file name"
    )
    parser.add_argument(
        "--gamedata", type=str, default="example", help="Game data file name"
    )
    parser.add_argument(
        "--wait_time_for_ack",
        type=float,
        default=60.0,
        help="Wait time for acknowledgement from Game App",
    )
    args = parser.parse_args()

    run_game(
        mock_action=args.mock,
        game_data_file_name=args.gamedata,
        external_websocket_server=args.external_websocket_server,
        wait_time_for_ack=args.wait_time_for_ack,
    )
