import datetime

from lyfe_agent.base import BaseState

# def describe_location(location):
#     if location.destination and location.arrival:
#         return f"at the {location.destination}"
#     elif location.destination and not location.arrival:
#         return f"on the way to {location.destination}"
#     else:
#         return "on the street"


def describe_location(location):
    # set location name
    if location.destination:
        prefix = "" if location.type == "person" else "the "
        location_name = prefix + location.destination
    else:
        location_name = ""

    # arrival logic
    if location.type == "place":
        if location.destination and location.arrival:
            return f"at {location_name}"
        elif location.destination and not location.arrival:
            return f"on the way to {location_name}"
        else:
            return "on the street"
    elif location.type == "person":
        if location.destination and location.arrival:
            if location.found:
                return f"with {location_name}"
            elif location.destination and not location.arrival:
                return f"looking for {location_name}"
            else:
                # temporary since agents are not fully location aware
                return "on the street"
        return "on the street"
    else:
        return "on the street"


class SimpleState(BaseState):
    falsy = {
        list: [],
        str: "",
        dict: {},
        bool: False,
        int: 0,
        "list": [],
        "str": "",
        "dict": {},
        "bool": False,
        "int": 0,
    }

    def __init__(self, data=None, datatype=None):
        if data is not None:
            self._data = data
        else:
            self.datatype = datatype if datatype is not None else str
            self._data = self.falsy[self.datatype]

    @property
    def data(self):
        return self._data

    def update(self, value):
        self._data = value


class NewEventDetector(SimpleState):
    def __init__(self, data=None, datatype=None):
        super().__init__(data, datatype)
        if data is None:
            data = True
        self._data = (data, "initialization")  # kick off the first slow_forward

    @property
    def data(self):
        return self._data[0]

    def update(self, new_event, source_reason=None):
        if source_reason is None:
            self._data = (new_event, "not given")
        else:
            self._data = (new_event, source_reason)


class CurrentOption(BaseState):
    def __init__(self, option_name, option_goal, action=None):
        self.option_name = option_name
        self.option_goal = option_goal

    def update(self, option_name, option_goal=None):
        self.option_name = option_name
        if option_goal:
            self.option_goal = option_goal

    @property
    def data(self):
        return {"option_name": self.option_name, "option_goal": self.option_goal}

    def is_same(self, option):
        for key in self.data:
            if self.data[key] != option.data[key]:
                return False
        return True


class Location(BaseState):
    def __init__(self, arrival=False, destination=None):
        self.arrival = arrival
        self.destination = destination
        # can be a place or a person
        self.type = None
        self.found = False

    def update(
        self, arrival=None, destination=None, type="place", nearby_creature=None
    ):
        self.type = type
        if arrival:
            self.arrival = arrival
        if destination:
            self.destination = destination
        if self.type == "person" and nearby_creature:
            self.found = self.destination in nearby_creature.data
