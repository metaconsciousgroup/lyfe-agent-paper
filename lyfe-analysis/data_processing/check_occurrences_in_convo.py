import pickle
from typing import Dict
import json

from .split_conversation_by_agent import ConversationItem, Conversation


def check_occurrences_in_convo(
    pickle_path: str, word1: str, word2: str = None
) -> Dict[str, Dict[str, int]]:
    """
    Load the pickle file and count the occurrences of two words in the same conversation item for each key.
    """
    # Load the pickle file
    with open(pickle_path, "rb") as f:
        data_dict = pickle.load(f)

    result = {}

    # Iterate over each key in the dictionary
    for key, conversations in data_dict.items():
        success_time = 0
        total_convo_number = len(conversations)
        detailed_info = []

        # For each key, iterate over the list of Conversation objects
        for conversation in conversations:
            # For each Conversation, check each ConversationItem
            for convo_item in conversation.conversation_list:
                if word2 is None:
                    if word1 in convo_item.response:
                        success_time += 1
                        detailed_info.append(
                            {"agent": convo_item.agent, "response": convo_item.response}
                        )
                elif word1 in convo_item.response and word2 in convo_item.response:
                    success_time += 1
                    detailed_info.append(
                        {"agent": convo_item.agent, "response": convo_item.response}
                    )

        result[key] = {
            "total_convo_number": total_convo_number,
            "occurrences_in_convo": success_time,
            "details": detailed_info,
        }

    result = post_check_occurrences_in_convo(result)

    return result


def post_check_occurrences_in_convo(result):
    # 1. check if occurrence_in_convo is 0
    for agent_name, data in result.items():
        data["in_memory"] = False
        data["in_summary"] = False

        if data["occurrences_in_convo"] == 0:
            data["hear_from_any"] = False
            data["hear_from_agent_name"] = None
            data.pop("details")
            continue

        data["hear_from_any"] = True
        data["hear_from_agent_name"] = list(
            {detail["agent"] for detail in data["details"]}
        )
        data.pop("details")

    return result


def check_in_memory(agent_memory_json, occurrence_result, word1, word2=None):
    """
    Check if the agent's memory contains the word.
    """
    with open(agent_memory_json) as f:
        agent_memory = json.load(f)

    for agent_name, data in occurrence_result.items():
        if data["hear_from_any"] and agent_name in agent_memory:
            if word2 is None:
                if any(
                    word1 in item
                    for memory_type in ["recentmem", "longmem"]
                    for item in agent_memory[agent_name][memory_type]
                ):
                    occurrence_result[agent_name]["in_memory"] = True
            elif any(
                word1 in item and word2 in item
                for memory_type in ["recentmem", "longmem"]
                for item in agent_memory[agent_name][memory_type]
            ):
                occurrence_result[agent_name]["in_memory"] = True

    return occurrence_result
