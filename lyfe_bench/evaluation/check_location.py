from datetime import datetime
from typing import Callable, Dict, List, Optional

Agent = Callable[[Dict[str, str]], Dict[str, str]]

def check_location(
    history: Dict[str, List],
    agents: List[Agent],
    location: str,
    start_time: str,
    end_time: Optional[str] = None,
    format="%m/%d/%Y %H:%M:%S"
):
    """
    Checks which agents from a specified list are present at a given location within a specified time range.

    Parameters:
    - history (Dict[str, List[Tuple[str, str]]]): A dictionary where keys are entity identifiers (str) and values are lists of tuples. Each tuple contains a timestamp (str) and a location (str). The timestamps should be in the format specified by the 'format' parameter.
    - agents (List[Agent]): A list of agents (of type Agent) to check for in the history. Only entities that are instances of Agent will be considered.
    - location (str): The location to check for the presence of agents.
    - start_time (str): The start of the time range for checking, as a string in the specified format.
    - end_time (str): The end of the time range for checking, as a string in the specified format.
    - format (str, optional): The format of the timestamps in the history and the start/end time parameters. Defaults to "%m/%d/%Y %H:%M:%S".

    Returns:
    - List[str]: A list of the identifiers of agents who were present at the specified location within the specified time range.

    This function parses the start and end times using datetime.strptime with the provided format, then iterates through the history. For each entity in the history that is also in the agents list, it checks if the entity's recorded locations and times fall within the specified location and time range. If so, the entity's identifier is added to the list of entities present.

    Example:
    history = {
        "Agent001": [("01/23/2024 10:00:00", "LocationA"), ("01/23/2024 12:00:00", "LocationB")],
        "Agent002": [("01/23/2024 11:00:00", "LocationA")]
    }
    agents = ["Agent001", "Agent002"]
    entities_present = check_location(history, agents, "LocationA", "01/23/2024 09:00:00", "01/23/2024 11:30:00")
    print(entities_present)  # Output: ["Agent001", "Agent002"]
    """
    entities_present = []
    start_time = datetime.strptime(start_time, format)
    if end_time is not None:
        end_time = datetime.strptime(end_time, format)

    for entity, entity_history in history.items():
        present = False
        for (time, locations) in entity_history:
            if entity not in agents:
                continue
            for time, loc in locations:
                time = datetime.strptime(time, format)
                if loc == location and start_time <= time:
                    if end_time is None or time <= end_time:
                        present = True
        if present:
            entities_present.append(entity)
    return entities_present

    