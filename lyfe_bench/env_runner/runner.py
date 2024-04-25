"""Env runner that turns a pettingzoo/websocket environment into a standalone process."""

import asyncio
import websockets
import json
import time
from typing import Any, Dict, List, Callable
from collections import defaultdict
from asyncio import Queue
import logging
from lyfe_bench.environments.base import BaseMultiAgentEnv


logger = logging.getLogger(__name__)

# TODO: Move this beautiful code somewhere more permanent, agent-api?

MESSAGE_TYPE_KEY = "message_type"
AGENT_ID_KEY = "agent_id"
DATA_KEY = "data"


class EnvRunner:
    """
    Environment runners that connects a pettingzoo-like multi-agent environment with an agent server that expose through a websocket server.

    The runner is responsible for converting observations from the environment to formats that the agents can understand, and
    converting actions from the agents to formats that the environment can understand.

    If there are more agent actions than the environment can handle, the runner will handle the overflow by dropping the extra actions by default.
    Other types of overflow can be provided by the user.
    """

    def __init__(
        self,
        make_env: Callable[..., BaseMultiAgentEnv],
        websocket_url: str,
        overflow: str = "drop",
        frame_rate=60,
    ) -> None:
        """
        Initialize the environment runner.

        Args:
            env: The PettingZoo-like environment object.
            websocket_url: URL of the websocket server to connect to agents.
            overflow: Strategy for handling when more actions are received than the environment can process.
            frame_rate: The frame rate at which the environment should run.
        """
        self._make_env = make_env

        self.websocket_url = websocket_url
        self.overflow_strategy = overflow
        self._frame_interval = 1.0 / frame_rate

        self.websocket: websockets.WebSocketClientProtocol = None

        # First message from web socket is received
        self._first_message = None

        # Create a queue for each agent to store their actions
        self.actions_queues: Dict[(str, Queue)] = defaultdict(Queue)

    async def _connect_to_websocket(self) -> None:
        """Connect to the WebSocket server."""
        self.websocket = await websockets.connect(self.websocket_url)
        logger.info("Connected to WebSocket.")

    async def _send_observation(
        self, agent_id: str, observation: Dict[str, Any]
    ) -> None:
        """Send observations to agents through WebSocket."""
        for key, val in observation.items():
            # TODO: Validate if key is a valid message type

            # Convert the observation into a JSON string
            message = json.dumps(
                {MESSAGE_TYPE_KEY: key, AGENT_ID_KEY: agent_id, DATA_KEY: val}
            )
            await self.websocket.send(message)

    async def _receive_actions(self) -> None:
        """Receive actions from agents through WebSocket and add them to the queue."""
        # Get a single message from the WebSocket
        async for json_message in self.websocket:
            # Convert the message into a Python dictionary
            message = json.loads(json_message)

            if self._first_message is None:
                self._first_message = message
                logger.info(f"Environment data received: {message}")
                continue

            # TODO: Validate if message has at least three keys
            action_queue: Queue = self.actions_queues[message[AGENT_ID_KEY]]
            await action_queue.put(message)

    # TODO: Name can be improved
    async def _process_actions(self) -> Dict[str, Any]:
        """Process and return actions from the queue according to the overflow strategy.

        Retrieves all actions from the queue, applies the overflow strategy, and clears the queue.

        Returns:
            actions: A dictionary of actions for each agent.
        """
        # Actions for all agents
        actions = defaultdict()
        for agent_id, action_queue in self.actions_queues.items():
            # For each agent queue, get all actions and clear the queue
            agent_actions = []
            while not action_queue.empty():
                agent_actions.append(await action_queue.get())

            # Apply the overflow strategy
            agent_action = self._apply_overflow_strategy(agent_actions)

            actions[agent_id] = agent_action

        return actions

    def _apply_overflow_strategy(self, actions: List[Any]) -> Any:
        """
        Apply the overflow strategy to the list of actions.

        Args:
            actions: A list of actions to process.

        Returns:
            The action to be processed based on the overflow strategy.
        """
        # TODO: This needs to be greatly improved, revisit!!

        if not actions:
            return None  # or a default action, depending on your environment's requirements

        # Example for a 'drop' strategy, adjusting as needed
        if self.overflow_strategy == "drop":
            # For simplicity, we take the oldest action and ignore the rest
            return actions[0]
        else:
            # Implement other strategies as needed
            return actions[0]  # Default to the oldest action for simplicity

    async def _init_env(self):
        """Initialize the environment.

        This function waits for the first message, and then initializes the environment using the first message.
        """
        # Wait until first message is not None, then use first message to initialize environment
        while self._first_message is None:
            await asyncio.sleep(0.1)
        env_data = self._first_message  # Assuming first message is the environment data
        # TODO: Validate if first message is a valid environment data
        self.env = self._make_env(**env_data)
        # Send an acknowledgment back to the communicator
        await self.websocket.send(json.dumps({MESSAGE_TYPE_KEY: "ack"}))

    async def run(self) -> None:
        """Run the environment-agent loop."""
        await self._connect_to_websocket()
        # Start listening for actions in a background task
        asyncio.create_task(self._receive_actions())

        # Initialize the environment
        await self._init_env()

        try:
            self.env.reset()
            i = 0
            while True:
                i += 1
                if i % 100 == 0:
                    logger.info(f"Frame {i}.")
                loop_start = time.time()

                # Get observation for each agent
                for agent_id in self.env.agent_ids:
                    observation = self.env.observe(agent_id)
                    # Send the observation to the agent (through communicator)
                    await self._send_observation(agent_id, observation)

                # Get all actions from agents
                actions = await self._process_actions()
                for agent_id, action in actions.items():
                    self.env.step(agent_id, action)

                # Ensure the environment runs at most at the frame rate
                loop_end = time.time()
                loop_duration = loop_end - loop_start
                sleep_duration = max(0, self._frame_interval - loop_duration)
                await asyncio.sleep(sleep_duration)

        except Exception as e:
            logger.info(f"An error occurred: {e}")
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the environment runner and close WebSocket connection."""
        self._first_message = None

        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket connection closed.")

        self.env.close()
        logger.info("Environment closed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Example usage
    # Assuming you have an `env` object and a WebSocket URL
    env_runner = EnvRunner(BaseMultiAgentEnv, "ws://localhost:8765")
    asyncio.run(env_runner.run())
