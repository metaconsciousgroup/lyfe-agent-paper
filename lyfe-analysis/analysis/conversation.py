"""Analyzing conversation environments."""
import pandas as pd
from pathlib import Path
import json

from analysis import log_to_csv
from analysis.analysis_utils import (
    process_hydra_folders_recursively,
    log_to_usage,
    log_to_agents,
    get_conversation,
    generate_dialogues_json,
)
import analysis.analysis_utils as analysis_utils
import analysis.plot_utils as plot_utils
from lyfe_agent.utils.name_utils import name_higher2lower

DEMOGRAPHICS_KEYS = [
    "First Name",
    "Last Name",
    "Age",
    "Gender",
    "City",
    "Occupation",
    "Personality",
    "Hobby",
    "Pet",
]


@process_hydra_folders_recursively
def post_process(path: Path, min_dialogue_len=3):
    """Post-processing after a multi-run."""
    log_filename = path / "main.log"

    # Get main_log and conversations CSV
    log_df, conv_df = log_to_csv(log_filename)
    log_df.to_csv(path / "main_log.csv")
    conv_df.to_csv(path / "conversation.csv")

    # Get agent specific log
    log_to_agents(log_filename, output_path=path)

    # Get dialogues; must send in TALK-only dataframe
    dialogues = generate_dialogues_json(conv_df, min_dialogue_len)

    # Save the dialogues dictionary as a JSON file
    with open(path / "dialogues.json", "w") as f:
        json.dump(dialogues, f, indent=4)

    # talks = get_conversation_json(conv_df, min_dialogue_len)
    # # Save the dialogues dictionary as a JSON file
    # with open(path / "talks.json", "w") as f:
    #     json.dump(talks, f, indent=4)

    try:
        # Get summary measurements & demographics
        cfg = analysis_utils.get_hydra_config(path)

        # Determine agents present in the multi-run
        unique_agents = set(list(log_df["agent"].unique()))
        demographics_list = []

        for agent_name in unique_agents:
            outputs = analysis_utils.get_hydra_overrides(path)
            agent_key = name_higher2lower(agent_name).replace(" ", "_")
            outputs["agent"] = agent_name
            if agent_key not in cfg["agents"]["dict"]:
                # prevent the player from being added to analysis
                continue
            agent_cfg = cfg["agents"]["dict"][agent_key]

            for demo_key in DEMOGRAPHICS_KEYS:
                demo_key = demo_key.replace(" ", "_").lower()
                demo_val = agent_cfg.get(demo_key, None) or agent_cfg["innate"].get(
                    demo_key, None
                )
                output_key = f"agent_{demo_key}"
                if demo_val is not None:
                    outputs[output_key] = demo_val

            demographics_list.append(outputs)

        # Generate summary demographics & multi-run DF
        summary_demographics = pd.DataFrame(demographics_list)
        summary_conv = (
            log_df.groupby(["agent", "event"]).size().reset_index(name="Count")
        )
        # Do a cross-join between multi-run and demographics
        summary = pd.merge(summary_demographics, summary_conv).drop("agent", axis=1)

        summary.to_csv(path / "summary.csv", index=False)
    except:
        print("Not a hydra path")

    # # Get LLM usage -- DEPRACATED
    # usage_df = log_to_usage(log_filename)
    # if len(usage_df) > 0:
    #     usage_df.to_csv(path / 'lm_usage.csv')

    # # Get measurements -- DEPRACATED
    # outputs['len_conv'] = len(conv_df)  # length of conversation
    # if len(usage_df) > 0:
    #     outputs['completion_tokens'] = sum(usage_df["Completions"])
    #     outputs['prompt_tokens'] = sum(usage_df["Prompts"])


def load_summary(path):
    summary_df = pd.read_csv(path / "multirun_summary.csv")
    return summary_df


def get_summary(path):
    summary_df = analysis_utils.concatenate_csv_files(path, "summary.csv")
    summary_df.to_csv(path / "multirun_summary.csv", index=False)
    return summary_df


def add_hobby_to_summary(path):
    """Special function for analyzing the hobby experiment.

    First get the hobby of all agents,
    then add a column to summary about the hobby of each agent
    """
    # TODO: Need better way to get this
    HOBBY_DICT = {
        "Alice Smith": "music",
        "Bob Jones": "music",
        "Carla Wilson": "sport",
        "Dave Miller": "sport",
        "Emma Jackson": "music",
        "Frank Brown": "music",
        "Grace Lee": "sport",
        "Harry Johnson": "sport",
    }

    summary_df = load_summary(path)

    hobbies = list()
    # for agents in summary_df['agents']:
    #     # CSV file stores agents as string, need converting back to list
    #     agents = ast.literal_eval(agents)
    #     # map to hobby
    #     tmp_hobby = [HOBBY_DICT[agents[0]], HOBBY_DICT[agents[1]]]
    #     tmp_hobby.sort()
    #     hobbies.append(tmp_hobby)

    for tmp_hobby in zip(summary_df["agent1_hobby"], summary_df["agent2_hobby"]):
        tmp_hobby = list(tmp_hobby)
        tmp_hobby.sort()
        hobbies.append(tmp_hobby)

    # for tmp_hobby in summary_df[['agent1_hobby', 'agent2_hobby']]:
    #     print(tmp_hobby)
    #     tmp_hobby.sort()
    #     hobbies.append(tmp_hobby)
    #
    summary_df["hobbies"] = hobbies
    summary_df.to_csv(path / "multirun_summary.csv", index=False)
    return summary_df


def add_hobby_pet_gender_to_summary(path):
    """Special function for analyzing the hobby and pet."""

    summary_df = load_summary(path)

    hobbies = list()

    for tmp_hobby in zip(summary_df["agent1_hobby"], summary_df["agent2_hobby"]):
        tmp_hobby = list(tmp_hobby)
        tmp_hobby.sort()
        hobbies.append(tmp_hobby)

    pets = list()

    for tmp_pet in zip(summary_df["agent1_pet"], summary_df["agent2_pet"]):
        tmp_pet = list(tmp_pet)
        tmp_pet.sort()
        pets.append(tmp_pet)

    genders = list()

    for tmp_gender in zip(summary_df["agent1_gender"], summary_df["agent2_gender"]):
        tmp_gender = list(tmp_gender)
        tmp_gender.sort()
        genders.append(tmp_gender)

    summary_df["hobbies"] = hobbies
    summary_df["pets"] = pets
    summary_df["genders"] = genders
    summary_df.to_csv(path / "multirun_summary.csv", index=False)
    return summary_df


if __name__ == "__main__":
    # path = Path('../multirun/2023-05-02/18-52-20')
    path = Path("../multirun/2023-05-03/11-34-48")

    post_process(path)
    get_summary(path)
    add_hobby_pet_gender_to_summary(path)

    summary_df = load_summary(path)

    plot_utils.connection_graph(summary_df)

    plot_utils.plot_distribution(summary_df, "len_conv", "hobbies", save_fig=True)
    plot_utils.plot_distribution(summary_df, "len_conv", "pets", save_fig=True)
    plot_utils.plot_distribution(summary_df, "len_conv", "genders", save_fig=True)
    plot_utils.plot_groupby(
        summary_df,
        columns_to_group=["hobbies", "pets", "genders"],
        column_values="len_conv",
    )
