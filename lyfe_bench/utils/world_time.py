"""
utils related to the environment time
"""
from datetime import datetime, timedelta

class WorldTime:
    """
    Mutable world time object. A light wrapper around `datetime.datetime`.
    We require this class because `datetime.datetime` is immutable, which means that objects sharing a `datetime` object
    cannot make shared updates to their `datetime.datetime` object.
    """
    # def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: float = 0.):
    #     self.time = datetime(year, month, day, hour, minute, second)
    def __init__(self, time: str):
        self.time = datetime.strptime(time, "%m/%d/%Y %H:%M:%S")
    
    def __iadd__(self, delta_time: float):
        self.time += timedelta(seconds=delta_time)
        return self
    
    def __add__(self, delta_time: float):
        return WorldTime(self.time + timedelta(seconds=delta_time))
    
    def __str__(self):
        return self.format_str()
    
    def format_str(self, format="%m/%d/%Y %H:%M:%S"):
        return self.time.strftime(format)
