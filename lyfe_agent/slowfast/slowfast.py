import concurrent.futures
from concurrent.futures import Future
from threading import Lock
import datetime
import random

import logging
from lyfe_agent.utils.log_utils import log_error
from typing import Any

logger = logging.getLogger(__name__)

COMPLETION_TIMEOUT = 5.0  # in seconds
INCOMPLETION_TIMEOUT = 10.0  # in seconds


class SlowFastModule:
    """
    This module consists of a slow module and a fast module
    """

    def __init__(
        self, executor, name, slow_func, fast_func, slow_on=True, log_slow_func_io=False
    ):
        """
        Initialize the AgentThreading instance.

        The module consists of a slow function and a fast function.
        The slow function is executed in a separate thread and the fast function is executed in the main thread.
        The slow function is executed only when the slow trigger function returns True.
        The slow function is executed only once at a time.
        The slow function is executed only when the previous slow function is completed.
        The slow function is executed only when the slow_on flag is True.

        :param executor: ThreadPoolExecutor for running on a separate thread.
        :param name: Name of the process ('slow_fast_sys' or 'state').
        :param slow_func: Function to execute that takes a long time.
        :param fast_func: Function to generate a fast result.
        :param slow_on: Whether to use the slow function or not.
        :param log_slow_func_io: Whether to log the inputs and outputs of the slow function.
        """
        self.executor = executor

        self.name = name
        self.slow_func = slow_func
        self.fast_func = fast_func
        self._slow_on = slow_on

        self._log_slow_func_io = log_slow_func_io
        self._slow_function_io_log = []

        # to avoid getting spammed by the logger
        self._last_log_time = None

        self._initialize_threading_variables()

    def _initialize_threading_variables(self):
        self._latest_slow_result = None
        self._result_lock = Lock()
        self._future = Future()
        self._future.set_result(None)
        self._slow_result_first_avail = True
        self._count = 0
        self._time_submit_slow_func = datetime.datetime.now() + datetime.timedelta(
            seconds=random.uniform(-0.5, 0.5)
        )
        self._current_input = None

    def get_result(self, inputs):
        with self._result_lock:
            # Default is to use results from Slow func, if not avail, use Fast func
            output = self._latest_slow_result or self.fast_func(inputs)
            self._latest_slow_result = None
        return output

    def can_submit_slow_func(self, suspended_time=0.0) -> bool:
        """Determines if a new slow func should be submitted for execution."""
        time_since_last_run = (
            datetime.datetime.now() - self._time_submit_slow_func
        ).total_seconds()
        enough_time_passed = time_since_last_run >= suspended_time
        return self._slow_on and self._future.done() and enough_time_passed

    def submit_slow_func(self, inputs):
        """Submit a new slow func for execution."""
        logger.debug(f"[SLOW FAST] Submitting slow func for {self.name} {inputs}")
        try:
            self._current_input = inputs  # Save the input
            self._future = self.executor.submit(self.slow_func, inputs)
            self._time_submit_slow_func = datetime.datetime.now()
            self._count += 1
            self._slow_result_first_avail = (
                True  # When slow result first becomes available
            )
        except Exception as e:
            logger.error(
                f"[SLOW FAST] Exception during {self.name} process because of {e}"
            )

    def retrieve_result(self):
        """
        Retrieve the result of the slow function. If the task isn't completed within a
        timeout or if an error occurs, log the respective messages.
        """
        if not self._slow_on:
            return

        if self._future.done():
            if self._slow_result_first_avail:
                self._handle_completed_task()
                self._slow_result_first_avail = False
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
                    log_error(
                        self,
                        f"{self.name} result retrieval timed out after {COMPLETION_TIMEOUT}",
                        exc=e,
                    )
                )
                self._latest_slow_result = None
            except Exception as e:
                logger.error(
                    log_error(self, f"Exception during {self.name} process", exc=e)
                )
                self._latest_slow_result = None

    def _handle_incomplete_task(self):
        time_since_last_run = (
            datetime.datetime.now() - self._time_submit_slow_func
        ).total_seconds()
        if not self._future.cancelled() and time_since_last_run > INCOMPLETION_TIMEOUT:
            current_time = datetime.datetime.now()
            if self._last_log_time is None or (current_time - self._last_log_time).total_seconds() > 10.0:
                logger.error(
                    log_error(
                        self,
                        f"{self.name} process timed out after {time_since_last_run}s.",
                    )
                )
                self._last_log_time = current_time
            self._latest_slow_result = None
            self._slow_result_first_avail = False
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
