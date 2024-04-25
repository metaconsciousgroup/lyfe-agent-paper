"""Helper function to converting name formats."""

from difflib import SequenceMatcher
from typing import List, Tuple


def format_name(name: str):
    """Helper function to format names before comparison."""
    if name is None:
        return "[NONE]"
    return name.lower().strip()


def name_match(
    name: str, exact_names: List[str], threshold: float = 0.2
) -> Tuple[bool, str]:
    """
    Determines if a given name roughly matches any names in a list of exact names.

    Args:
        name (str): The name to be matched.
        exact_names (List[str]): A list of exact names to be matched against.
        threshold (float, optional): The similarity threshold to consider a match.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean value indicating if a match is found
                          and the matched exact name, or None if no match is found.
    """
    formatted_name = format_name(name)

    best_similarity = 0
    best_match = None

    for exact_name in exact_names:
        similarity = SequenceMatcher(
            None, formatted_name, format_name(exact_name)
        ).ratio()

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = exact_name

    if best_similarity > threshold:
        return True, best_match

    return False, None


def name_include(target: str, keywords_list: List[str]) -> Tuple[bool, str]:
    """
    Determines if the target string is a substring of any string in the keywords_list.

    Note that this is case insensitive.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean value indicating if a match is found and the matched keyword, or None if no match is found.
    """
    for keyword in keywords_list:
        if keyword.lower() in target.lower():
            return True, target
    return False, target


def name_lower2higher(name: str) -> str:
    """Convert name from lower to title case.

    Will convert a name of form john_smith to John Smith
    """
    return " ".join(name.split("_")).title() if name != "[NONE]" else None


def name_higher2lower(name: str) -> str:
    """Convert name from title case to our lower case format.

    Will convert a name from John Smith to john_smith
    Note that this assumes that there is no space in last name
    """
    if name is None:
        return None
    name_parts = name.split()
    # Convert the first two parts to lowercase and join them with a space
    firstname_parts = " ".join(name_parts[:-1]).lower()
    # Convert the last part to lowercase and join it to the second part with an underscore
    lastname_part = name_parts[-1].lower()
    lower_name = f"{firstname_parts}_{lastname_part}"
    return lower_name


def check_name_fit_format(name):
    higher_name = name_lower2higher(name)
    lower_name = name_higher2lower(higher_name)
    higher_name2 = name_lower2higher(lower_name)
    lower_name2 = name_higher2lower(higher_name2)
    assert higher_name == higher_name2
    assert lower_name == lower_name2


def get_map_unity2actual_name(unity_agents: list, agent_names: list) -> dict:
    """Map list of Unity agent names to our agent name."""
    map_unity2actual_name = {}
    for i, unity_agent in enumerate(unity_agents):
        map_unity2actual_name[unity_agent] = agent_names[
            int(unity_agent.split("=")[-1])
        ]
    return map_unity2actual_name
