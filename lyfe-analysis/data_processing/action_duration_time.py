import json
from datetime import datetime
from collections import defaultdict


def collect_time_and_action_func(path):
    with open(path, "r") as f:
        data = json.load(f)

    # Use defaultdict to easily collect data per name
    grouped_data = defaultdict(list)

    for entry in data:
        time = entry["input"]["time"]
        name = entry["input"]["name"]
        time_obj = datetime.strptime(time, "%m/%d %H:%M")
        action_func = entry["input"]["active_func"]

        grouped_data[name].append((time_obj, action_func))

    return dict(grouped_data)  # Convert back to standard dictionary


def calculate_average_duration(grouped_data):
    # Dictionary to store the average durations for each agent
    agent_durations = {}

    for agent, time_action_pairs in grouped_data.items():
        durations = defaultdict(list)
        sorted_pairs = sorted(time_action_pairs, key=lambda x: x[0])  # Sort by time

        prev_time, prev_action = sorted_pairs[0]
        session_start_time = prev_time

        for curr_time, curr_action in sorted_pairs[1:]:
            if curr_action != prev_action:
                # If current action is different from previous one, calculate duration
                session_duration = (
                    curr_time - session_start_time
                ).total_seconds() / 60  # Convert to minutes
                durations[prev_action].append(session_duration)

                session_start_time = curr_time  # Start a new session for the new action
            prev_time, prev_action = curr_time, curr_action

        # Handle the duration of the last action session
        session_duration = (
            prev_time - session_start_time
        ).total_seconds() / 60  # Convert to minutes
        durations[prev_action].append(session_duration)

        average_durations = {}
        for action, duration_list in durations.items():
            if duration_list:  # Check if list is not empty to prevent ZeroDivisionError
                avg_duration = sum(duration_list) / len(duration_list)
                average_durations[action] = round(avg_duration, 3)
        agent_durations[agent] = average_durations

    # count average duration for each action acorss all agents
    all_actions = defaultdict(list)
    for agent, durations in agent_durations.items():
        for action, duration in durations.items():
            all_actions[action].append(duration)
    for action, duration_list in all_actions.items():
        if duration_list:
            avg_duration = sum(duration_list) / len(duration_list)
            all_actions[action] = round(avg_duration, 3)
    all_actions["unit"] = "minutes"
    all_actions["criterion"] = "in-world time"
    return all_actions


def action_duration_time_calculation(path):
    time_action_pairs = collect_time_and_action_func(path)
    avg_durations = calculate_average_duration(time_action_pairs)
    return avg_durations
