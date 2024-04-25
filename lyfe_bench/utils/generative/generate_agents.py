"""Generate agents automatically using language models."""
import re
import yaml
import numpy as np
import pandas as pd
import geopandas as gpd
import random

from agent.utils.name_utils import name_lower2higher
from agent.embedding_utils import match_query_idx
from generative.generate_utils import DATABASEPATH, AGENTCONFIGPATH, UNITYWORLDPATH
from generative.generate_utils import get_resource_embeddings


def generate_demographics(cfg, lm):
    """Generate demographics for agents."""
    question = ', '.join(cfg.types)

    _content = f"Generate demographics information for {cfg.num_agents} people for a fictional story. Don't Contain Any Enumerations. "
    if cfg.diverse:
        _content += "The demographics should be as diverse as possible."
    _content += f"Specify their {question}. Don't give 'nan' as an answer."

    if 'content' in cfg:
        _content = _content + cfg.content

    messages = [
        {'role': 'system',
         'content': "Respond to the user request. Do not provide extra information. "
                    "Output your response in a csv format. Do not include header."},
        {'role': 'user',
         'content': _content
         }
    ]
    # Get response from language model
    reply = lm(messages)

    # Clean the response
    cleaned_reply = []
    for line in reply.split('\n'):
        cleaned_line = ','.join([val.strip(' ') for val in line.split(',')])
        cleaned_reply.append(cleaned_line)
    cleaned_reply = '\n'.join(cleaned_reply)

    header = ','.join(cfg.types) + '\n'
    demographics = header + cleaned_reply

    while len(demographics.splitlines()) != cfg.num_agents + 1:

        # Get response from language model
        reply = lm(messages)

        # Clean the response
        cleaned_reply = []
        for line in reply.split('\n'):
            cleaned_line = ','.join([val.strip(' ') for val in line.split(',')])
            cleaned_reply.append(cleaned_line)
        cleaned_reply = '\n'.join(cleaned_reply)

        header = ','.join(cfg.types) + '\n'
        demographics = header + cleaned_reply

    print('Generated demographics')
    print(demographics)

    file_name = DATABASEPATH / (cfg.name + '_demographics.csv')
    print('Saving demographics to ', file_name)
    with open(file_name, 'w') as csv_file:
        csv_file.write(demographics)


def generate_workmem(lm, content: str, memory_length = 100) -> list:
    # Generate working memory sentences
    messages = [
        {'role': 'system',
         'content': "Generate a few sentences describing the working memory of a person, "
                    "which includes active and recent events or observations. Use first-person perspective. "
                    f"Use only exactly {memory_length} words."},
        {'role': 'user',
         'content': content}
    ]
    reply = lm(messages)
    workmem_sentences = paragraph_to_sentences(reply)
    return workmem_sentences


def generate_recentmem(lm, content: str, memory_length = 100) -> list:
    # Generate recent memory sentences
    messages = [
        {'role': 'system',
         'content': "Generate a few sentences describing the recent memory of a person, "
                    "which includes things they are likely to do throughout a day. Use first-person perspective. "
                    f"Use only exactly {memory_length} words."},
        {'role': 'user',
         'content': content}
    ]
    reply = lm(messages)
    recentmem_sentences = paragraph_to_sentences(reply)
    return recentmem_sentences


def generate_longmem(lm, content: str, memory_length = 100) -> list:
    # Generate long-term memory sentences
    messages = [
        {'role': 'system',
         'content': "Generate a few sentences describing the long-term memory of a person, "
                    "which includes high-level and abstract information like personality traits "
                    "and significant events that greatly affect their personality. Use first-person perspective. "
                    f"Use only exactly {memory_length} words."},
        {'role': 'user',
         'content': content}
    ]
    reply = lm(messages)
    longmem_sentences = paragraph_to_sentences(reply)
    return longmem_sentences


def generate_background_story(demographic_df: pd.DataFrame, lm) -> dict:
    """Generate background story for one person."""
    df = demographic_df
    # Set agent dict according to demography
    agent = dict()
    content = ''
    # for demographic_df
    for key, val in df.items():
        new_key = key[:]
        new_key = new_key.replace(' ', '_')
        new_key = new_key.lower()
        if isinstance(val, np.integer):
            val = int(val)
        agent[new_key] = val

        content += f"This person's {key} is {val}. "
    print('Generating background story for...')
    print(content)

    # Threshold for how many words could be used to write the memory
    memory_length = 100 
    
    agent['workmem'] = generate_workmem(lm, content, memory_length = memory_length)
    agent['recentmem'] = generate_recentmem(lm, content, memory_length = memory_length)
    agent['longmem'] = generate_longmem(lm, content, memory_length = memory_length)

    return agent


def generate_background_stories(cfg, lm):
    """Generate background stories for all agents. Format as config yaml."""
    # Load demographics
    path = DATABASEPATH / (cfg.demographics_name + '_demographics.csv')
    print('Load demographics from ', path)
    demographics_df = pd.read_csv(path)

    agents_dict = dict()
    for i in range(len(demographics_df)):
        agent = generate_background_story(demographics_df.iloc[i], lm)

        agent_key = agent['first_name'].lower() + '_' + agent['last_name'].lower()
        agents_dict[agent_key] = agent

    agents = {'name': cfg.name, 'dict': agents_dict}

    # Save to both database and configs/agents/
    file_name = AGENTCONFIGPATH / (cfg.name + '_gen_agents.yaml')
    print('Save background stories to ', file_name)
    with open(file_name, 'w') as yaml_file:
        yaml.dump(agents, yaml_file)

    file_name = DATABASEPATH / (cfg.name + '_gen_agents_copy.yaml')
    print('Save background stories to ', file_name)
    with open(file_name, 'w') as yaml_file:
        yaml.dump(agents, yaml_file)


def paragraph_to_sentences(paragraph: str) -> list:
    """Split paragraph to sentence."""
    sentences = re.findall(r'\s*[^.!?]*[.!?]', paragraph)
    return [s.strip() for s in sentences if s.strip()]


def generate_agent_layout(cfg_environment, cfg_agents):
    environment_layout = gpd.read_file(UNITYWORLDPATH / f"{cfg_environment.name}_layout.geojson")

    agent_locations = []
    for _ in range(cfg_agents.demographics.num_agents):
        agent_placed = False

        while not agent_placed:
            x = random.uniform(environment_layout.total_bounds[0], environment_layout.total_bounds[2])
            y = random.uniform(environment_layout.total_bounds[1], environment_layout.total_bounds[3])
           
            agent_point = gpd.points_from_xy([x], [y])[0]

            # note: the last item in the environment_layout is the village boundary
            if not any(b.geometry.contains(agent_point) for i in range(len(environment_layout) - 1) for b in [environment_layout.iloc[i]]):
                agent_locations.append(agent_point)
                agent_placed = True

    # Saving agent location
    agent_gpd = gpd.GeoDataFrame(geometry=agent_locations)
    file_name = AGENTCONFIGPATH / (cfg_agents.stories.name + '_gen_agents.yaml')
    with open(file_name, "r") as f:
        agent_data = yaml.safe_load(f)
    agent_gpd["name"] = [agent[0] for agent in agent_data["dict"].items()]
    agent_gpd["display_name"] = [name_lower2higher(name) for name in agent_gpd["name"]]
    agent_gpd["feature_type"] = "agent"

    # Get information about Resources
    print("Matching agent demographics to prefabs")
    prefab_paths = list()
    resource_df = get_resource_embeddings()
    people_df = resource_df[resource_df["type"] == "People"]
    for agent_info in agent_data["dict"].values():
        agent_info_query = f"A {agent_info['age']} year old {agent_info['gender']} {agent_info['occupation']}"
        idx, _ = match_query_idx(people_df, agent_info_query)
        print(agent_info_query, people_df.iloc[idx]["path"])
        prefab_paths.append(people_df.iloc[idx]["path"])

    agent_gpd["prefab_path"] = prefab_paths

    agent_gpd.to_file(UNITYWORLDPATH / (cfg_agents.stories.name + "_layout.geojson"), driver='GeoJSON')
    print('Saved agent layout')


