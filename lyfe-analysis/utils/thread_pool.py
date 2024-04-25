# In your utils.thread_pool file
import os
from concurrent.futures import ThreadPoolExecutor
import logging
import threading

logger = logging.getLogger(__name__)


def determine_thread_count():
    """Determine the number of threads to use for the ThreadPoolExecutor."""
    possible_thread = 8
    total_thread = os.cpu_count() * possible_thread
    logger.debug(f"Total thread count: {total_thread}")
    return total_thread


def start_executor() -> ThreadPoolExecutor:
    logger.info(
        f"Initializing ThreadPoolExecutor with {determine_thread_count()} threads"
    )
    return ThreadPoolExecutor(max_workers=determine_thread_count())


def shutdown_executor(executor: ThreadPoolExecutor):
    """Shutdown ThreadPoolExecutor."""
    executor.shutdown(wait=True)
    logger.debug(f"ThreadPoolExecutor shut down, ID: {id(executor)}")
