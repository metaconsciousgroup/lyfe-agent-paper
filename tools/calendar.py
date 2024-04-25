import bisect
import datetime

from tools.base import Tool
class Event:
    def __init__(self, start_time, end_time, buffer_time, content):
        self.start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        self.end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
        self.content = content
        self.alert_time = self.start_time - datetime.timedelta(minutes=buffer_time)
        self.alarm_on = True
        self.alarm_ring = False

    def __str__(self):
        return f"Event: {self.content} from {self.start_time} to {self.end_time}"

    def __lt__(self, other):
        return self.start_time < other.start_time

    def conflicts_with(self, other_event):
        return self.start_time < other_event.end_time and self.end_time > other_event.start_time

class Calendar(Tool):
    available_actions = [
        "add_event", 
        "get_events",
        "snooze alarm",
        "turn off alarm",
    ]

    def __init__(self):
        self.upcoming_events = []
        self.past_events = []
        self.current_time = None

    def add_event(self, event):
        position = bisect.bisect_left(self.upcoming_events, event)
        if position > 0 and event.conflicts_with(self.upcoming_events[position-1]):
            return f"Conflict with previous event: {self.upcoming_events[position-1]}"
        if position < len(self.upcoming_events) and event.conflicts_with(self.upcoming_events[position]):
            return f"Conflict with next event: {self.upcoming_events[position]}"
        self.upcoming_events.insert(position, event)
        return "Event added successfully."

    def get_events(self):
        return [str(event) for event in self.upcoming_events]

    # # Might want to change output
    # def update(self, new_time):
    #     self.current_time = datetime.datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S')
        
    #     # Check if there is an upcoming event and if its alert time has arrived
    #     if self.upcoming_events and self.upcoming_events[0].alert_time <= self.current_time:
    #         if self.upcoming_events[0].alarm_on:
    #             self.upcoming_events[0].alarm_ring = True
    #             return self.upcoming_events[0]
        
    #     return None
    
    def update(self, observations):
        new_time = observations["time"]
        self.current_time = datetime.datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S')
        
        # Check if there is an upcoming event and if its alert time has arrived
        if self.upcoming_events and self.upcoming_events[0].alert_time <= self.current_time:
            event = self.upcoming_events[0]
            if event.alarm_on:
                event.alarm_ring = True
                if observations.get("tools") is None:
                    observations["tools"] = {}
                event_details = {
                    "start_time": event.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "end_time": event.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "content": event.content,
                    "alarm_ring": event.alarm_ring,
                }
                observations["tools"].update({"calendar": event_details})        
        return observations

    def snooze_alarm(self):
        if self.upcoming_events and self.upcoming_events[0].alarm_ring:
            event = self.upcoming_events[0]
            event.alarm_ring = False
            event.alert_time = event.alert_time + datetime.timedelta(minutes=5)
            if event.alert_time > event.end_time:
                event.alert_time = event.end_time

    def turn_off_alarm(self):
        if self.upcoming_events and self.upcoming_events[0].alarm_ring:
            event = self.upcoming_events.pop(0)            
            event.alarm_ring = False
            event.alarm_on = False
            self.past_events.append(event)