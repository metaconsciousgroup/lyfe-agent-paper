from lyfe_agent.base import BaseState

class EventTracker(BaseState):
    def __init__(self, signal=False, update_frequency=1):
        self._count = 0

        self.update_frequency = update_frequency
        # becomes true after `update_frequency` events pass
        self.signal = signal

    def receive(self, value):
        if value:
            self._count += 1
        
        if self._count >= self.update_frequency:
            self.signal = True

    def get(self):
        if self.signal:
            self._count = 0
            self.signal = False
            return True
        return False