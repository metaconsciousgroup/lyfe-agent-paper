
from typing import List

class ItemSystem:
    """
    Manages the locations of items in the environment.
    """
    def __init__(self, items, locations: List):
        self.items = items
        self.locations = locations
        self.data = {item: location for item, location in zip(items, locations)}

    def __call__(self, item):
        return self.data[item]

    def update(self, item, location):
        self.data[item] = location

    def send_message(self, sender, message):
        """
        Note that there is no receiver
        """
        self.data[sender] = message

    def receive_messages(self, receiver):
        observables = {item: location for item, location in self.data.items() if location in self.nearby_creature(receiver)}
        return observables