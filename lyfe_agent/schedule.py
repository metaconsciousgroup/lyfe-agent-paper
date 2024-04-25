from datetime import datetime, timedelta


class Schedule:
    def __init__(self, initial_schedule=None):
        """
        Initializes the Schedule with a given initial_schedule or an empty one.
        """
        self.current_time = "01/01 06:00"
        self.schedule = [
            self._get_formatted(event) for event in (initial_schedule or [])
        ]

    def _get_formatted(self, event_data):
        """
        Formats the provided event data, setting default metadata if necessary.
        """
        metadata = event_data.get("metadata", {})
        metadata.setdefault("type", "generic")
        metadata.setdefault("time", self.current_time)
        return {"content": event_data.get("content"), "metadata": metadata}

    @staticmethod
    def _is_time_less_than(time1, time2):
        """
        Compares two time strings and returns True if time1 is less than time2.
        """
        return datetime.strptime(time1, "%m/%d %H:%M") < datetime.strptime(
            time2, "%m/%d %H:%M"
        )

    def add_event(self, content, event_type="generic", expire_time=None):
        """
        Adds an event to the schedule.
        """
        if not expire_time:
            expire_time_dt = datetime.strptime(
                self.current_time, "%m/%d %H:%M"
            ) + timedelta(minutes=30)
            expire_time = expire_time_dt.strftime("%m/%d %H:%M")

        self.schedule.append(
            {
                "content": content,
                "metadata": {
                    "time": self.current_time,
                    "type": event_type,
                    "expire_time": expire_time,
                },
            }
        )

    def add_event_from_list(self, event_list):
        """
        Adds a list of events to the schedule.
        event_list only contains content, not metadata.
        """
        for event in event_list:
            self.add_event(event)

    def get_event(self, time_str):
        """
        Retrieves an event from the schedule based on the provided time string.
        """
        return next(
            (event for event in self.schedule if event["metadata"]["time"] == time_str),
            None,
        )

    def remove_event(self, time_str):
        """
        Removes an event from the schedule based on the provided time string.
        """
        self.schedule = [
            event for event in self.schedule if event["metadata"]["time"] != time_str
        ]

    def update(self, new_time):
        """
        Updates the schedule by removing any expired events.
        """
        self.current_time = new_time
        self.schedule = [
            event
            for event in self.schedule
            if not (
                event["metadata"].get("expire_time")
                and self._is_time_less_than(
                    event["metadata"]["expire_time"], self.current_time
                )
            )
        ]

    @property
    def current_goal(self):
        """
        Returns the current goal which is the first event in the schedule.
        """
        return (
            self.schedule[0]["content"]
            + " at "
            + self.schedule[0]["metadata"]["time"]
            + "."
            if self.schedule
            else "Need to plan for future!!!"
        )

    @property
    def current_goal_time(self):
        """
        Returns the time of the current goal.
        """
        return self.schedule[0]["metadata"]["time"] if self.schedule else None

    @property
    def is_empty(self):
        """
        Returns True if the schedule is empty.
        """
        return len(self.schedule) == 0
