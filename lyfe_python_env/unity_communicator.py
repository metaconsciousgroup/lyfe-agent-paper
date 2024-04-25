from abc import ABC, abstractmethod
import asyncio
import logging
import threading
import websockets
import websocket
from collections import deque

logger = logging.getLogger(__name__)


class WebsocketWrapper(ABC):
    def __init__(self, websocket_url, websocket_port):
        self._websocket_url = websocket_url
        self._websocket_port = websocket_port

        self._message_handler = None
        self._incoming_message_process_task = None
        self._incoming_message_process_thread = None
        self._incoming_messages = deque(maxlen=1000)  # Queue for incoming messages
        self._incoming_messages_count = 0
        self._processed_incoming_messages_count = 0
        self._running = False

    def start(self):
        self._running = True
        self._start_impl()

    @abstractmethod
    def _start_impl(self):
        pass

    def stop(self):
        self._running = False
        if self._incoming_message_process_task:
            self._incoming_message_process_task.cancel()
        if self._incoming_message_process_thread:
            self._incoming_message_process_thread.join()
        self._stop_impl()

    @abstractmethod
    def _stop_impl(self):
        pass

    @abstractmethod
    def send_text_message(self, message):
        pass

    def get_stats(self):
        basic_stats = {
            "running": self._running,
            "incoming_messages_count": self._incoming_messages_count,
            "processed_incoming_messages_count": self._processed_incoming_messages_count,
        }
        additional_stats = self._get_additional_stats()
        return {**basic_stats, **additional_stats}

    @abstractmethod
    def _get_additional_stats(self):
        pass

    def set_message_handler(self, handler):
        if self._message_handler:
            logger.warning("A handler is already set, skipping")
            return
        self._message_handler = handler

        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._incoming_message_process_task = loop.create_task(
                self._process_incoming_messages()
            )
            loop.run_forever()  # Run the loop until stop() is called

        if (
            not self._incoming_message_process_task
            or self._incoming_message_process_task.done()
        ):
            self._incoming_message_process_thread = threading.Thread(
                target=run_in_thread
            )
            self._incoming_message_process_thread.start()

    async def _process_incoming_messages(self):
        logger.info("Starting to process incoming messages")
        while self._running:
            if self._incoming_messages and self._message_handler:
                message = self._incoming_messages.popleft()
                self._message_handler(message)
                self._processed_incoming_messages_count += 1
        logger.info("Stopped processing incoming messages")

    def receive_message(self, message):
        self._incoming_messages_count += 1
        self._incoming_messages.append(message)
        if len(self._incoming_messages) >= 1000:
            logger.warning("Incoming message queue is full, dropping messages")


class StandaloneWebsocketServerWrapper(WebsocketWrapper):
    def __init__(self, websocket_url, websocket_port):
        super().__init__(websocket_port=websocket_port, websocket_url=websocket_url)
        self._outgoing_messages = deque(maxlen=1000)  # Queue for outgoing messages
        self._outgoing_messages_count = 0
        self._processed_outgoing_messages_count = 0

        self._server_thread = None
        self._websocket_server = None
        self._websocket_client = None

    def run_server(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        start_server = websockets.serve(
            self.handler,
            self._websocket_url,
            self._websocket_port,
            ping_interval=180,
            ping_timeout=30,
        )
        loop = asyncio.get_event_loop()
        self._websocket_server = loop.run_until_complete(start_server)
        loop.run_forever()

    def _start_impl(self):
        self._server_thread = threading.Thread(target=self.run_server)
        self._server_thread.start()

    def _stop_impl(self):
        if self._websocket_server:
            self._websocket_server.close()
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._websocket_server.wait_closed())
            loop.stop()
        if self._server_thread:
            self._server_thread.join()  # Wait for the server thread to finish

    def send_text_message(self, message):
        logger.debug(f"Preparing to send message: {message}")
        self._outgoing_messages_count += 1
        self._outgoing_messages.append(message)
        if len(self._outgoing_messages) >= 1000:
            logger.warning("Outgoing message queue is full, dropping messages")
        if len(self._outgoing_messages) > 5:
            logger.info(
                f"Outgoing message queue size: {len(self._outgoing_messages)} last message: {message}"
            )

    def get_incoming_message_queue(self):
        return list(self._incoming_messages)

    async def process_outgoing_messages(self, websocket):
        while self._running:
            if (
                self._outgoing_messages
                and self._websocket_client
                and self._websocket_client.open
            ):
                message = self._outgoing_messages.popleft()
                await websocket.send(message)
                self._processed_outgoing_messages_count += 1
            await asyncio.sleep(0.005)  # Allows handling of other tasks

    async def handler(self, websocket, path):
        self._websocket_client = websocket
        client_address = websocket.remote_address[0]  # Get the client's IP address
        logging.info(f"Client connected: {client_address}")
        try:
            # Run tasks for processing incoming and outgoing messages concurrently
            outgoing_task = asyncio.create_task(
                self.process_outgoing_messages(websocket)
            )
            incoming_task = asyncio.create_task(self.process_incoming(websocket))
            await asyncio.gather(outgoing_task, incoming_task)
        finally:
            logger.info(f"Client disconnected: {client_address}")
            self._websocket_client = None

    async def process_incoming(self, websocket):
        async for message in websocket:
            self.receive_message(message)

    def _get_additional_stats(self):
        return {
            "outgoing_messages_count": self._outgoing_messages_count,
            "processed_outgoing_messages_count": self._processed_outgoing_messages_count,
        }


class ExternalWebsocketServerWrapper(WebsocketWrapper):
    def __init__(self, websocket_url, websocket_port, simulation_id="01234"):
        super().__init__(websocket_port=websocket_port, websocket_url=websocket_url)
        self._simulation_id = simulation_id
        self._websocket_client = None
        self._incoming_message_accumulate_thread = None

        self._outgoing_messages_count = 0

    def _start_impl(self):
        try:
            self._websocket_client = websocket.create_connection(
                f"ws://{self._websocket_url}:{self._websocket_port}/agent-observations?simulation_id={self._simulation_id}"
            )
            self._incoming_message_accumulate_thread = threading.Thread(
                target=self._process_incoming
            )
            self._incoming_message_accumulate_thread.start()
        except Exception as e:
            logger.error(f"Failed to connect to the websocket server: {e}")
            raise e

    def _stop_impl(self):
        if self._incoming_message_accumulate_thread:
            self._incoming_message_accumulate_thread.join()

    def _process_incoming(self):
        try:
            while True:
                message = self._websocket_client.recv()
                if message is None:
                    break
                self.receive_message(message)

        except websocket.WebSocketConnectionClosedException:
            logging.error("WebSocket connection closed.")
        except Exception as e:
            logging.error(f"Error in receiving message: {e}")
        finally:
            if self._websocket_client:
                self._websocket_client.close()

    def send_text_message(self, message):
        if self._websocket_client:
            self._websocket_client.send(message)
            self._outgoing_messages_count += 1
        else:
            raise ConnectionError("Websocket connection is not established.")

    def _get_additional_stats(self):
        return {
            "outgoing_messages_count": self._outgoing_messages_count,
        }
