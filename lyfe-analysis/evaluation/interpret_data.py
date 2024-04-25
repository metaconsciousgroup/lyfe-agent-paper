import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from settings import BASE_DIR

MULTIRUN_DIR = os.path.join(BASE_DIR, "multirun")
EVALUATION_DIR = os.path.join(BASE_DIR, "evaluation")


def extract_pickle(pickle_path):
    # Check if file exists
    if not os.path.isfile(pickle_path):
        print(f"No file found at {pickle_path}")
        return None

    # Open and load the pickle file
    with open(pickle_path, "rb") as f:
        data = pickle.load(f)

    return data


def logs_plot(logs_data):
    # Categories (tasks)
    categories = list(logs_data.keys())

    # Calculate success rate percentages for each category
    success_rates = [
        100 * (value["success"] / value["total"]) for value in logs_data.values()
    ]

    # Create a bar plot
    x = np.arange(len(categories))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects = ax.bar(x, success_rates, width)

    # Add labels, title, and custom x-axis tick labels
    ax.set_xlabel("Tasks")
    ax.set_ylabel("Success Rate (%)")
    ax.set_title("Performance based on obtain_info logs")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)

    # Set the y-axis limits
    ax.set_ylim([0, 100])

    # Save the plot to the file
    plt.savefig(EVALUATION_DIR + "/obtain_info_performance_plots/logs_plot.png")

    # Show the plot
    plt.show()


def agents_interview_plot(agents_data):
    # Categories (agents)
    categories = list(agents_data.keys())

    # Calculate success rate percentages for the 'who_is_owner' task for each agent
    success_rates = [
        100 * (value["who_is_owner"]["success"] / value["who_is_owner"]["total"])
        for value in agents_data.values()
    ]

    # Create a bar plot
    x = np.arange(len(categories))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects = ax.bar(x, success_rates, width)

    # Add labels, title, and custom x-axis tick labels
    ax.set_xlabel("Agents")
    ax.set_ylabel("Success Rate (%)")
    ax.set_title("Does agent know who is the owner?")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)

    # Set the y-axis limits
    ax.set_ylim([0, 100])

    # Save the plot to the file
    plt.savefig(
        EVALUATION_DIR + "/obtain_info_performance_plots/agents_interview_plot.png"
    )

    # Show the plot
    plt.show()


def agent_memory_plot(agents_data):
    # Initialize an empty dictionary to store success rates
    success_rates = {}

    # Iterate over agents_data to gather success rates for each agent and memory type
    for agent, data in agents_data.items():
        if "is_question_asked_in_memory" in data:
            # Categories (memory types)
            categories = list(data["is_question_asked_in_memory"].keys())
            success_rates[agent] = {
                "categories": categories,
                "rates": [
                    100 * (value["success"] / value["total"])
                    if "success" in value and "total" in value
                    else 0
                    for value in data["is_question_asked_in_memory"].values()
                ],
            }

    # Create a bar plot for each agent
    for agent, info in success_rates.items():
        x = np.arange(len(info["categories"]))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        rects = ax.bar(x, info["rates"], width)

        # Add labels, title, and custom x-axis tick labels
        ax.set_xlabel("Memory Type")
        ax.set_ylabel("Success Rate (%)")
        ax.set_title(f"Is relevant info in memory of {agent}")
        ax.set_xticks(x)
        ax.set_xticklabels(info["categories"])

        # Set the y-axis limits
        ax.set_ylim([0, 100])

        # Save the plot to the file
        plt.savefig(
            EVALUATION_DIR + "/obtain_info_performance_plots/{agent}_memory_plot.png"
        )

        # Show the plot
        plt.show()


# Define the file path
logs_file_path = MULTIRUN_DIR + "/2023-07-27/18-09-32/eval_multirun_logs.pkl"
agents_file_path = MULTIRUN_DIR + "/2023-07-27/18-09-32/eval_multirun_agents.pkl"

# Import the data and extract
logs_data = extract_pickle(logs_file_path)
agents_data = extract_pickle(agents_file_path)

# Create and save plots
logs_plot = logs_plot(logs_data)
agents_interview_plot = agents_interview_plot(agents_data)
agent_memory_plot = agent_memory_plot(agents_data)
