
import functools
import logging
import time

try:
    from matplotlib import pyplot as plt
except ImportError:
    plt = None

logger = logging.getLogger(__name__)


def time_decorate(storage_dict):
    """Decorator generator that uses an external dictionary for storing timings."""
    def actual_decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time

            # Append the elapsed time to the function's list of timings in storage_dict
            if func.__name__ not in storage_dict:
                storage_dict[func.__name__] = []
            storage_dict[func.__name__].append(elapsed_time)

            return result
        return wrapper
    return actual_decorator


class CodeTimer:
    def __init__(self, callback, name, enable_monitoring=True):
        self.callback = callback
        self.name = name
        self.enable_monitoring = enable_monitoring

    def __enter__(self):
        if self.enable_monitoring:
            self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enable_monitoring:
            elapsed_time = time.time() - self.start_time
            self.callback(self.name, elapsed_time)


def plot_timings(timings):
    """Save the time series of timings for each function using an external timings dictionary."""
    if not timings or not isinstance(timings, dict) or timings == {}:
        return
    
    if plt is None:
        logger.error("matplotlib not installed. Skipping plotting. Install with `pip install matplotlib`")
        return

    # Plot with all functions together
    plt.figure(figsize=(10, 6))
    for func_name, time_list in timings.items():
        plt.plot(time_list, label=func_name)

    plt.ylabel('Time (seconds)')
    plt.xlabel('Calls')
    plt.title('All Function Timings Together')
    plt.legend()
    plt.savefig("all_functions_together.png")
    plt.close()

    # Individual plots for each function
    for func_name, time_list in timings.items():
        plt.figure(figsize=(10, 6))
        plt.plot(time_list, label=func_name)
        plt.ylabel('Time (seconds)')
        plt.xlabel('Calls')
        plt.title(f'Timings for {func_name}')
        plt.legend()
        plt.savefig(f"{func_name}_timing.png")
        plt.close()


class ProfilingMeta(type):
    EXCLUDED_METHODS = set(['_record_timing', 'plot_timings'])

    def __new__(cls, name, bases, attrs):
        for key, value in attrs.items():
            if callable(value) and not key.startswith("__") and key not in ProfilingMeta.EXCLUDED_METHODS:
                attrs[key] = ProfilingMeta._wrap_with_timer(value, key)
        return super(ProfilingMeta, cls).__new__(cls, name, bases, attrs)

    @staticmethod
    def _wrap_with_timer(func, func_name):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            with ProfilingMeta.CodeTimer(self, func_name):
                return func(self, *args, **kwargs)
        return wrapper

    class CodeTimer:
        def __init__(self, instance, func_name):
            self.instance = instance
            self.func_name = func_name

        def __enter__(self):
            if self.instance._enable_monitoring:
                self.start_time = time.time()

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.instance._enable_monitoring:
                elapsed_time = time.time() - self.start_time
                full_name = f"{self.instance.__class__.__name__}.{self.func_name}"
                self.instance._record_timing(full_name, elapsed_time)


class BaseProfilingClass(metaclass=ProfilingMeta):
    def __init__(self, enable_monitoring=False):
        self._enable_monitoring = enable_monitoring
        self._timings_storage = {}

    def _record_timing(self, name, elapsed_time):
        self._timings_storage.setdefault(name, []).append(elapsed_time)

    def plot_timings(self):
        logger.info(
            f"Plotting timings for {self.__class__.__name__} {self._timings_storage.keys()}")
        if self._enable_monitoring:
            try:
                plot_timings(self._timings_storage)
            except Exception as e:
                logger.error(f"Error plotting timings: {e}")

# Ensure to define or import the 'plot_timings' function as referenced in the BaseProfilingClass
