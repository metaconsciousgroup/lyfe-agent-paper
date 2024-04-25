from collections import deque
import copy
from lyfe_agent.base import BaseState


class OptionHistory(BaseState):
    def __init__(self, max_size=10):
        """Store a history of actions taken by the agent."""
        self.history = deque(maxlen=max_size)

    @property
    def data(self):
        return list(self.history)

    @property
    def last_option(self):
        return self.history[-1] if self.history else None

    def update(self, current_option):
        if current_option.option_name == "cognitive_controller":
            return

        # avoid adding the same action twice
        if not self.last_option or (
            self.last_option and not self.last_option.is_same(current_option)
        ):
            # NOTE: must use copy here to avoid modifying the action in-place
            self.history.append(copy.copy(current_option))
