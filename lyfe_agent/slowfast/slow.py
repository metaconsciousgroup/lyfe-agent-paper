import concurrent.futures
from concurrent.futures import Executor, Future
from threading import Lock
import datetime
import random

import logging
from lyfe_agent.utils.log_utils import log_message, log_error
from typing import Any

logger = logging.getLogger(__name__)

COMPLETION_TIMEOUT = 5.0  # in seconds
INCOMPLETION_TIMEOUT = 10.0  # in seconds


class SlowBlockModule:
    """
    This module consists of a slow procedure that happens on the current thread.

    Note: If the task will take a long time, use SlowThreadModule instead.
    """

    def __init__(self, name, slow_func, slow_on=True, log_slow_func_io=False):
        """
        Initialize the SlowBlockModule instance.

        :param name: Name of the module.
        :param slow_func: Function to execute that takes a long time.
        :param slow_on: Whether to use the slow function or not.
        :param log_slow_func_io: Whether to log the inputs and outputs of the slow function.
        """
        self.name = name
        self.slow_func = slow_func
        self._slow_on = slow_on
        self._log_slow_func_io = log_slow_func_io
        self._slow_function_io_log = []
        self._result_lock = Lock()
        self._latest_slow_result = None

    @property
    def slow_on(self):
        return self._slow_on

    def set_slow_on(self, slow_on):
        self._slow_on = slow_on

    def execute_slow_func(self, inputs=None):
        """Executes the slow function and retrieves its result."""
        if self._slow_on:
            try:
                self._latest_slow_result = self.slow_func(option=self.name)

                if self._log_slow_func_io:
                    # Log the input-output pair
                    self.log_io_pair(inputs, self._latest_slow_result)

            except Exception as e:
                logger.error(f"Exception during {self.name} process because of {e}")
                self._latest_slow_result = None

    def get_result(self):
        """Fetches the latest result from the slow function."""
        with self._result_lock:
            output = self._latest_slow_result
            self._latest_slow_result = None
        return output

    def log_io_pair(self, input_data, output_data):
        """Logs the input and output data."""
        self._slow_function_io_log.append({"input": input_data, "output": output_data})

    def get_io_log(self):
        """Get the input-output log of the slow function."""
        return self._slow_function_io_log

    def clear_io_log(self):
        """Clear the input-output log of the slow function."""
        self._slow_function_io_log = []


class SlowThreadModule:
    """
    This module consists of a slow procedure that happens on a separate thread.
    """

    def __init__(
        self, executor: Executor, name, slow_func, slow_on=True, log_slow_func_io=False
    ):
        """
        Initialize the SlowThreadModule instance.

        The slow function is executed in a separate thread.
        The slow function is executed only once at a time.
        The slow function is executed only when the slow_on flag is True.
        """

        self.name = name
        self.slow_func = slow_func
        assert executor is not None, "Executor cannot be None."
        self._executor = executor
        self._slow_on = slow_on
        self._log_slow_func_io = log_slow_func_io
        self._slow_function_io_log = []

        self._initialize_threading_variables()

    def _initialize_threading_variables(self):
        self._latest_slow_result = None
        self._result_lock = Lock()
        self._future = Future()
        self._current_input = None
        self._future.set_result(None)
        self._time_submit_slow_func = datetime.datetime.now()

    def can_submit_slow_func(self, external_signal=False, suspended_time=0.0) -> bool:
        """Determines if a new slow func should be submitted for execution."""
        time_since_last_run = (
            datetime.datetime.now() - self._time_submit_slow_func
        ).total_seconds()
        enough_time_passed = time_since_last_run >= suspended_time
        return (
            self._slow_on
            and self._future.done()
            and external_signal
            and enough_time_passed
        )

    def submit_slow_func(self, inputs):
        """Submit a new slow func for execution."""
        if inputs is None or inputs == self._current_input:
            return
        logger.debug(f"[SLOW] Submitting slow func for {self.name} {inputs}")
        try:
            self._current_input = inputs  # Save the input
            self._future = self._executor.submit(self.slow_func, inputs)
            self._time_submit_slow_func = datetime.datetime.now()
        except Exception as e:
            logger.error(f"[SLOW] Exception during {self.name} process because of {e}")

    def get_result(self):
        with self._result_lock:
            if not self._future.done():
                return None

            output = self._latest_slow_result
            self._latest_slow_result = None
        return output

    def retrieve_result(self):
        """
        Retrieve the result of the slow function. If the task isn't completed within a
        timeout or if an error occurs, log the respective messages.
        """
        if not self._slow_on:
            return

        if self._future.done():
            self._handle_completed_task()
        else:
            self._handle_incomplete_task()

    def _handle_completed_task(self):
        with self._result_lock:
            try:
                self._latest_slow_result = self._future.result(
                    timeout=COMPLETION_TIMEOUT
                )

                if self._log_slow_func_io:
                    # Save the input-output pair to the log
                    self.log_io_pair(self._current_input, self._latest_slow_result)

            except concurrent.futures.TimeoutError as e:
                logger.error(
                    f"[SLOW] {self.name} result retrieval timed out after {COMPLETION_TIMEOUT}"
                )
                self._latest_slow_result = None
            except Exception as e:
                logger.error(f"[SLOW] Exception during {self.name} process")
                self._latest_slow_result = None

    def _handle_incomplete_task(self):
        time_since_last_run = (
            datetime.datetime.now() - self._time_submit_slow_func
        ).total_seconds()

        if not self._future.cancelled() and time_since_last_run > INCOMPLETION_TIMEOUT:
            logger.error(
                f"[SLOW] {self.name} process timed out after {time_since_last_run}s."
            )
            self._latest_slow_result = None
            self._future.cancel()

    def log_io_pair(self, input_data, output_data):
        """Logs the input and output data."""
        self._slow_function_io_log.append({"input": input_data, "output": output_data})

    def get_io_log(self):
        """Get the input-output log of the slow function."""
        return self._slow_function_io_log

    def clear_io_log(self):
        """Clear the input-output log of the slow function."""
        self._slow_function_io_log = []
