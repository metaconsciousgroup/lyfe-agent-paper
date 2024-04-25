from abc import ABC, abstractmethod
from typing import Dict, Union, List, Tuple, Any
import time
import logging
from queue import Queue
from threading import Lock, Event


import numpy as np
from omegaconf.listconfig import ListConfig
import openai
from openai.embeddings_utils import get_embeddings

logger = logging.getLogger(__name__)


class BaseEmbeddingMemory:
    """Base class for embedding memory storage systems."""

    def __init__(self):
        self._last_item = None

        # Threading utilities
        self.lock = Lock()
        self.query_embeddings = []
        self.query_event = Event()

    def is_repetitive(self, input_item):
        # TODO: This implementation is buggy. It's wrong if is_repetitive is not always called
        _is_repetitive = input_item == self._last_item
        self._last_item = input_item
        return _is_repetitive

    @property
    def items(self) -> List[str]:
        raise NotImplementedError

    @property
    def items_embeddings(self) -> List[str]:
        raise NotImplementedError

    @property
    def size(self) -> int:
        raise NotImplementedError

    def add(self, memory: str) -> None:
        raise NotImplementedError

    def fill_encoder_memories(self, embedding, memory_content):
        raise NotImplementedError

    def query(self, text: str, num_memories_retrieved: int = 1, timeout=5.0) -> List[str]:
        raise NotImplementedError

    def retrieve(self, num_memories_retrieved: int) -> List[str]:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError


class EncoderManager:
    """EncoderManager represents a module that manages encoding documents.

    It receives documents from various MemoryModules, processes them in batches,
    and sends the resulting embeddings back to the corresponding MemoryModules.

    Args:
        encoder_func (callable): a function that takes a list of documents and returns a list of embeddings

    Usage:
        EncoderManager is used by MemoryModules to encode documents.
        A MemoryModule must have self.memory_bank, self.embeddings,
        self.query_embeddings, and self.lock attributes.
    """

    def __init__(
        self,
        encoder_func,
        env_dict: Dict[str, str],
        executor=None,
        batch_size=10,
        max_wait_time=1.0,
    ):
        logger.info("Initializing EncoderManager...")
        assert env_dict is not None, "env_dict must be provided"
        assert env_dict["OPENAI_APIKEY"] is not None, "OPENAI_APIKEY must be provided"
        openai.api_key = env_dict["OPENAI_APIKEY"]
        self.queue = Queue()  # main queue for incoming documents
        self.query_queue = Queue()  # Additional queue for queries
        self.batch_size = batch_size  # maximum batch size for processing documents
        self.max_wait_time = max_wait_time  # maximum waiting time to form a batch
        self.encoder_func = encoder_func  # custom encoder function
        logger.info(f"Initializing EncoderManager with executor {executor}")
        self.executor = executor

        logger.debug("Testing encoder function...")
        output = self.encoder_func(["Testing"])
        logger.debug(f"Encoder function output: {output}")

        self._stop_event = Event()  # event to signal the thread to stop

        # To make a self-adjusted Encoder on max_wait_time
        # Initialize counters for both queues
        self.query_queue_counter = 0
        self.queue_counter = 0

        # Duration in seconds after which we will check the counters
        self.monitor_interval = 2.0

    def queue_mem(self, module: BaseEmbeddingMemory, 
                  key: str, value: Any = None):
        """Queue a document to be encoded.
        
        Args:
            module: the class that will hold the encoded embedding
            key: the memory key to be encoded
            value: the memory value to be stored
        """
        # The queue holds tuples of (type, module, data)
        self.queue.put(("doc", module, key, value))
        self.queue_counter += 1

    def queue_query(self, module: BaseEmbeddingMemory, query: Any):
        self.query_queue.put(("query", module, query, None))
        self.query_queue_counter += 1

    def monitor_queues(self):
        """Monitor the queues and adjust max_wait_time based on their frequencies."""
        total_items = self.query_queue_counter + self.queue_counter

        # Calculate frequency
        frequency = total_items / self.monitor_interval

        # Adjust max_wait_time based on the frequency
        if frequency > 8:  # high frequency
            # High frequency: There are many memory waiting to be added
            self.max_wait_time = min(1.0, self.max_wait_time * 1.1)
        elif frequency < 3:  # low frequency
            # Low frequency: Only query_queue is being used
            self.max_wait_time = max(0.05, self.max_wait_time * 0.7)

        # Reset counters
        self.query_queue_counter = 0
        self.queue_counter = 0

    def queue_runner(self):
        batch = []
        while not self._stop_event.is_set():
            start_time = time.time()
            # try to form a batch
            while len(batch) < self.batch_size:
                timeout = self.max_wait_time - (time.time() - start_time)
                if timeout < 0:
                    break
                item = self.fetch_item_from_queues(timeout)
                if item is not None:
                    batch.append(item)
                else:
                    # Sleeping is critical to prevent the while loop from hogging CPU
                    time.sleep(0.02)

            # if a batch is formed, process it using the custom encoder function
            # and send embeddings to the MemoryModules
            if batch:
                self.process_batch(batch)
            else:
                # Sleeping is critical to prevent the while loop from hogging CPU
                time.sleep(0.1)

    def fetch_item_from_queues(self, timeout):
        """Fetch item from queues with priority for query queue."""
        if not self.query_queue.empty():  # prioritize query queue
            return self.query_queue.get(timeout=timeout)
        elif not self.queue.empty():
            return self.queue.get(timeout=timeout)
        else:
            return None

    def process_batch(
            self, 
            batch: List[Tuple[str, BaseEmbeddingMemory, str, Any]]
        ):
        """Encode a batch and send embeddings to the MemoryModules.
        
        Args:
            batch: a list of tuples of (type, module, key, value)
        """
        logger.debug(f"Processing batch to be encoded. Batch size {len(batch)}...")
        embeddings = self.encoder_func([key for _type, module, key, val in batch])

        for (_type, module, key, val), embedding in zip(batch, embeddings):
            with module.lock:
                if _type == "doc":
                    module.fill_encoder_memories(embedding, val)
                elif _type == "query":
                    name = "" if not hasattr(module, "name") else module.name
                    # assuming 'retrieved' is a queue in MemoryModule
                    if type(embedding) == list:
                        module.query_embeddings.append(embedding)
                    else:
                        module.query_embeddings.append(embedding.tolist())
                    module.query_event.set()

        batch.clear()

    def run(self):
        """Start the encoding thread."""
        logger.info("Starting encoding thread...")
        try:
            # This organization allows for multiple queues to be run
            self.executor.submit(self.queue_runner)
        except Exception as e:
            logger.error(f"Exception during {self.name} process because of {e}")

        # Start the monitoring task in the executor with a delay
        self.monitor_executor()

    def monitor_executor(self):
        time.sleep(self.monitor_interval)
        self.monitor_queues()
        # check if self.executor is shutdown
        if not self._stop_event.is_set():
            self.executor.submit(self.monitor_executor)

    def stop(self):
        """Stop the encoding thread."""
        self._stop_event.set()


class EncoderCollection:
    """
    A collection of different encoders used in one simulation.
    """

    def __init__(self, models, rules, validation_config):
        """
        self.models: dict, key: model name, value: encoder model instance
        self.rule: dict, key: memory type, value: model's name
        """
        assert isinstance(validation_config, list), "validation_config must be a list"

        for mem_type in rules.keys():
            assert (
                mem_type in validation_config
            ), f"memory type {mem_type} not found in memory_modules.keys()"
        for model_name in rules.values():
            assert (
                model_name in models.keys()
            ), f"model name {model_name} not found in models.keys()"

        self.models = {name: model for name, model in models.items()}
        self.rules = rules

        self.multi_queue = {memory_type: [] for memory_type in self.rules.keys()}

    def step(self):
        for model in self.models.values():
            model.step()


class EmbeddingEncoder(ABC):
    """
    Base class for embedding encoders.
    """

    def __init__(self, model_name):
        self.model_name = model_name
        self.encoder = None
        self.dim = None

        self.storage = None

    @abstractmethod
    def __call__(self, text: Union[str, List[str]], **kwargs):
        return self.encoder(text, **kwargs)

    def receive(self, module, document):
        """
        Receive a text and add it to the index.
        """
        self.storage(document)  # need additional data

    # @abstractmethod
    # def deliver(self, module) -> None:
    #     module._on_deliver()

    def step(self) -> None:
        pass


class SentenceTransformerEncoder(EmbeddingEncoder):
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.encoder = self.model.encode
        self.dim = self("nonce").shape[-1]
        self.storage = {"embeddings": [], "memory_bank": []}

    def __call__(self, text: Union[str, List[str]], show_progress_bar: bool = False):
        return self.encoder(text, show_progress_bar=show_progress_bar)

    def queue_mem(self, module: BaseEmbeddingMemory, 
                  key: str, value: Any = None
        ):
        embedding = self([key])
        module.memory_bank.append(key)
        module.embeddings.append(embedding)

    def queue_query(self, module: BaseEmbeddingMemory, 
                    key: str, value: Any = None):
        embedding = self([key])
        module.query_embeddings.append(embedding)
        module.query_event.set()


class OpenAIEncoder(EmbeddingEncoder):
    def __init__(self, model_name):
        logger.info(f"Initializing OpenAI encoder with model {model_name}")
        self.model = model_name
        self.encoder = get_embeddings

    def __call__(self, text: Union[str, List[str]]):
        # TODO: There seems to be a bug here
        start_time = time.time()
        logger.debug(f"Calling OpenAI encoder with model {self.model}")
        results = np.array(self.encoder(text, engine=self.model))
        logger.debug(
            "OpenAI encoder finished in %.2f seconds" % (time.time() - start_time)
        )
        logger.debug(f"OpenAI encoder results: {results.shape}")
        return results
        # return np.array(self.encoder(text, engine=self.model))

    def queue_mem(self, module: BaseEmbeddingMemory, 
                  key: str, value: Any = None
        ):
        embedding = self([key])
        module.memory_bank.append(key)
        module.embeddings.append(embedding)

    def queue_query(self, module: BaseEmbeddingMemory, 
                    key: str, value: Any = None):
        embedding = self([key])
        module.query_embeddings.append(embedding)
        module.query_event.set()
