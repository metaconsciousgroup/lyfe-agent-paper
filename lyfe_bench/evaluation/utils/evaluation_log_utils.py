"""General utils for analyzing logs."""
from itertools import combinations
from pathlib import Path
import pandas as pd
import json
import re
from functools import wraps
import yaml
from collections import defaultdict

DEMOGRAPHICS_KEYS = ['First Name', 'Last Name', 'Age', 'Gender',
                     'City', 'Occupation', 'Personality', 'Hobby', 'Pet']
  
def process_hydra_folders_recursively(func):
    """Recursively search for folders and apply function.

    Recursively loop through folders in a path and
    apply function to each folder that contains a '.hydra' folder
    """
    @wraps(func)
    def wrapper(start_path: Path):
        if start_path.is_dir() and '.hydra' in [p.name for p in start_path.iterdir()]:
            func(start_path)
        for root in start_path.rglob('*'):
            if root.is_dir() and '.hydra' in [p.name for p in root.iterdir()]:
                func(root)
    return wrapper

def single_post_process(path, min_dialogue_len = 3, **kwargs):
    """Post-processing after a multi-run."""
    path = Path(path)
    log_filename = path / 'main.log'

    #Get main_log and conversations CSV
    log_df, conv_df = log_to_csv(log_filename)
    log_df.to_csv(path / 'main_log.csv', index=False)
    conv_df.to_csv(path / 'conversation.csv', index=False)

    #Get dialogues; must send in TALK-only dataframe
    dialogues = generate_dialogues_json(conv_df, min_dialogue_len)

    # Save the dialogues dictionary as a JSON file
    with open(path / 'dialogues.json', 'w') as f:
        json.dump(dialogues, f, indent=4)

@process_hydra_folders_recursively
def post_process(path, min_dialogue_len = 3, **kwargs):
    single_post_process(path, min_dialogue_len, **kwargs)
                     
def _parse_log_line(line):
    """Parse a single line in the log."""
    # Matching our log convention
    
    match_pattern = r'\[(.*?)\]\[(.*?)\]\[(.*?)\] - \[(.*?)\]\[(.*?)\]\[(.*?)\]\[(.*?)\](.*)'
    match = re.match(match_pattern, line.strip())

    if match:
        return match.groups()
    else:
        print(line)
        return None

def log_to_csv(filename):
    """Convert log to pandas dataframe."""
    with open(filename, "r") as f:
        lines = f.readlines()

    parsed_lines = list()
    parsed_lines_conv = list()
    for line in lines:
        result = _parse_log_line(line)
        if result is not None:
            parsed_lines.append(result)
            
            if any(word in result for word in ['TALK', 'MESSAGE']):
                parsed_lines_conv.append(result)

    #Extracts all possible events from main.log file
    log_df = pd.DataFrame(
        parsed_lines, columns=["timestamp", "source", "level", "agent", "event","gametime", "wildcard", "message"])
    
    #Extracts only the components where agents are communicating with each other
    conv_df = pd.DataFrame(
        parsed_lines_conv, columns=["timestamp", "source", "level", "sender", "event","gametime", "receiver", "message"])
    return log_df, conv_df

def log_to_agents(filename, output_path):
    """Store log for individual agents."""
    # Create a dictionary to store lines with unique names as keys
    lines_by_name = defaultdict(list)

    # Read the input file and populate the dictionary
    with open(filename, 'r') as infile:
        for line in infile:
            matches = re.findall(r'\[(.*?)\]', line)
            if len(matches) >= 4:
                name = matches[3]
                name = name_higher2lower(name)
                lines_by_name[name].append(line)

    Path.mkdir(output_path / "agents", exist_ok=True)
    # Write the lines to separate output files based on the unique names
    for name, lines in lines_by_name.items():
        output_file = output_path / "agents" / f"{name}.log"
        with open(output_file, 'w') as outfile:
            for line in lines:
                outfile.write(line)

def get_conversation(log_df: pd.DataFrame) -> pd.DataFrame:
    """For getting conversation."""
    conv_df = log_df[log_df['event'] == 'TALK']
    conv_df = conv_df[['agent', 'message']]
    return conv_df

def generate_dialogues_json(df, min_length=1):
    # Create an empty dictionary to store the dialogues
    dialogues = {}
    
    # Get a list of unique agent names from the 'sender' column of the dataframe
    agents = df['sender'].unique()

    # Use itertools.combinations to generate all pairs of agents
    for agent1, agent2 in combinations(agents, 2):
        # Select rows from the dataframe where either agent1 is the sender and agent2 is the receiver, or vice versa
        df_dialogue = df[((df['sender'] == agent1) & (df['receiver'] == agent2)) |
                         ((df['sender'] == agent2) & (df['receiver'] == agent1))]
        
        # Sort these rows based on timestamp to maintain the order of the conversation
        df_dialogue = df_dialogue.sort_values(by='timestamp')
        
        # Convert the 'message' column of these rows to a list to represent a dialogue
        dialogue = df_dialogue['message'].tolist()
        
        # Add the dialogue to the dictionary if its length is greater than or equal to the specified minimum length
        if len(dialogue) >= min_length:
            # The key is a string combining the two agent names, and the value is the dialogue list
            dialogues[f'Dialogue_{agent1}_{agent2}'] = dialogue
    
    # Return the dialogues dictionary
    return dialogues

def _format_override(hydra_path):
    """Helper function for formatting override from hydra.

    read every line of a yaml file, each line of the yaml file looks like
    `- general.seed=3`. Remove the `- ` at the beginning, and replace the `=` with `: `
    """
    input_yaml_file_path = hydra_path / 'overrides.yaml'
    output_yaml_file_path = hydra_path / 'tmp_overrides.yaml'

    with open(input_yaml_file_path, 'r') as input_file, open(output_yaml_file_path, 'w') as output_file:
        for line in input_file:
            if line.startswith('- '):
                line = line[2:]  # Remove '- ' at the beginning of the line
            line = line.replace('=', ': ')  # Replace '=' with ': '
            output_file.write(line)


def get_hydra_overrides(path: Path) -> dict:
    """Return a dict from the override.yaml from hydra"""
    hydra_path = path / '.hydra'
    assert hydra_path.is_dir()
    _format_override(hydra_path)
    with open(hydra_path / "tmp_overrides.yaml", "r") as stream:
        output = yaml.safe_load(stream)
    if not output:
        return {}
    return output


def get_hydra_config(path: Path):
    """Return a dict from the config.yaml from hydra"""
    hydra_path = path / '.hydra'
    assert hydra_path.is_dir()
    with open(hydra_path / "config.yaml", "r") as stream:
        output = yaml.safe_load(stream)
    return output


def concatenate_csv_files(folder_path, csv_file_name):
    """Concatenate all csv files that exist with a folder."""
    all_csv_files = list(folder_path.rglob(csv_file_name))
    dataframes = []

    for csv_file in all_csv_files:
        df = pd.read_csv(csv_file)
        dataframes.append(df)

    concatenated_df = pd.concat(dataframes, ignore_index=True)
    return concatenated_df