from collections import defaultdict
import json
import logging
import traceback
from typing import Any, List
import uuid
from lyfe_python_env import process_incoming
from lyfe_python_env.datatype.send_out import OutDataGame, OutDataScene
from lyfe_python_env.message_converters import convert_to_actions

from lyfe_python_env.time_decorator import (
    BaseProfilingClass,
)
from lyfe_python_env.unity_communicator import (
    ExternalWebsocketServerWrapper,
    StandaloneWebsocketServerWrapper,
    WebsocketWrapper,
)
from lyfe_python_env.unity_resources import UnityResources


logger = logging.getLogger(__name__)


class LyfeWebsocketWrapper(BaseProfilingClass):
    def __init__(
        self,
        game_data: dict = None,
        out_data_scene: OutDataScene = None,
        websocket_url="localhost",
        websocket_port=8765,
        simulation_id: str = None,
        enable_monitoring: bool = False,
        external_websocket_server: bool = False,
        **kwargs,
    ):
        BaseProfilingClass.__init__(self, enable_monitoring)
        self._unity_resource: UnityResources = UnityResources()
        if game_data is not None:
            unity_scene = self._unity_resource.create_scene_from_dict(game_data)
        elif out_data_scene is not None:
            unity_scene = out_data_scene
            self._unity_resource.register_agents(unity_scene)
        else:
            raise ValueError("Either `game_data` or `out_data_scene` must be provided.")
        game_data_command_id = str(uuid.uuid4())
        out_data_game = OutDataGame(
            commandId=game_data_command_id,
            clientAuth=False,
            scene=unity_scene,
        )

        logger.info("[SYSTEM] Starting websocket connection...")
        if external_websocket_server:
            assert simulation_id is not None
            self.websocket_wrapper: WebsocketWrapper = ExternalWebsocketServerWrapper(
                websocket_url,
                websocket_port,
                simulation_id=simulation_id,
            )
        else:
            self.websocket_wrapper: WebsocketWrapper = StandaloneWebsocketServerWrapper(
                websocket_url, websocket_port
            )

        self.websocket_wrapper.start()
        logger.info("[SYSTEM] Websocket connection established.")
        self.websocket_wrapper.send_text_message(self._to_json_dump(out_data_game))

        self._raw_agent_messages: defaultdict[str, List[Any]] = defaultdict(list)

        def message_handler(msg):
            try:
                observations = json.loads(msg)
                process_incoming.process_incoming(
                    observations, self._unity_resource, self._raw_agent_messages
                )
            except Exception as e:
                stack_trace = traceback.format_exc()
                logger.error(
                    f"Error in receiving message: {e}\nStack trace: {stack_trace}"
                )

        self.websocket_wrapper.set_message_handler(message_handler)

    # Test action sending, for `main.py`
    def send_test_action(self, agent_id, action):
        actions = convert_to_actions(action, agent_id)
        if actions is not None:
            for action in actions:
                self.websocket_wrapper.send_text_message(self._to_json_dump(action))

    def send_action(self, data):
        if data is not None:
            self.websocket_wrapper.send_text_message(self._to_json_dump(data))

    def _to_json_dump(self, data):
        text = data.model_dump_json(
            exclude_none=True,
        )
        return text

    def get_unity_resources(self) -> UnityResources:
        return self._unity_resource

    def get_observations(self, agent_id: str):
        raw_data = self.process_agent_messages(agent_id)
        return raw_data

    def process_agent_messages(self, agent_id) -> dict:
        """Process agent-specific messages from Unity in Environment Wrapper.

        :param agent_id: the current agent whose messages will be processed
        :param observation: the current observation who will be updated
        """
        agent_list = self._raw_agent_messages[agent_id]
        read_pointer = len(agent_list)
        raw_data = agent_list[:read_pointer]
        self._raw_agent_messages[agent_id] = agent_list[read_pointer:]
        return raw_data

    def close(self):
        self.websocket_wrapper.stop()

    def get_agent_id_list(self):
        return self._unity_resource.get_agent_id_list()

    def get_incoming_message_count(self):
        return self.websocket_wrapper.get_stats()["incoming_messages_count"]

    def plot_timings(self):
        # TODO implement this
        env_stats = self.websocket_wrapper.get_stats()
        logger.info(f"env_stats: {env_stats}")
