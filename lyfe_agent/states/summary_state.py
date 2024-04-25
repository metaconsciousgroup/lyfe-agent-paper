from lyfe_agent.base import BaseState
import threading


class SummaryState(BaseState):
    """
    SummaryState class provides a structured representation of summarized data.
    """

    def __init__(self, keys):
        self.summary_keys = list(keys)
        self.summary_details = {key: None for key in self.summary_keys}
        # make a separate self.summary so that it won't be affected by changes in summary_keys (NOTE: we probably will use SUMMARY as a key in parser_config)
        self.summary = ""
        # Initialize the lock
        self._lock = threading.Lock()

    @property
    def data(self):
        combined_data = (
            self.summary_details.copy()
        )  # Make a copy to not modify the original dictionary
        combined_data[
            "summary"
        ] = self.summary  # update the summary attribute with whole summary
        return combined_data

    def _update_summary(self):
        """
        Updates the summary attribute based on the current summary details.
        """
        if len(self.summary_keys) == 1:
            key = self.summary_keys[0]
            self.summary = self.summary_details[key]
        else:
            self.summary = "\n".join(
                f"- {key}: {self.summary_details[key]}" for key in self.summary_keys
            )

    def update(self, **kwargs):
        # Acquire the lock when updating attributes
        with self._lock:
            common_keys = set(self.summary_keys).intersection(kwargs)
            for key in common_keys:
                self.summary_details[key] = kwargs[key]
            # After updating, make sure the summary is also updated
            self._update_summary()
