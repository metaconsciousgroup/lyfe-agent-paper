from lyfe_agent.base import BaseState
from datetime import datetime, timedelta


class ExpireTimeDetector(BaseState):
    def __init__(self, delta_time=1, time_based_new_event=False):
        self.delta_time = timedelta(minutes=delta_time)
        self.record_action_time = {
            "option_name": None,
            "expire_time": datetime.now() + self.delta_time,
        }
        self.is_expired = False
        self.time_based_new_event = time_based_new_event

    def update(self, current_option=None):
        if (
            current_option
            and self.record_action_time["option_name"]
            != current_option.data["option_name"]
        ):
            self.record_action_time = {
                "option_name": current_option.data["option_name"],
                "expire_time": datetime.now() + self.delta_time,
            }
            self.is_expired = False

        if (
            self.time_based_new_event
            and datetime.now() > self.record_action_time["expire_time"]
        ):
            self.is_expired = True

    @property
    def data(self):
        return {
            "delta_time": self.delta_time.total_seconds()
            / 60,  # Convert timedelta to minutes
            "unit": "minute",
            "record_action_time": self.record_action_time,
            "time_based_new_event": self.time_based_new_event,
            "is_expired": self.is_expired,
        }
