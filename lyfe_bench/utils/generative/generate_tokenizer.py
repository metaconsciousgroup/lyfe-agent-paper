"""Generate simple tokenizer."""
from pathlib import Path
import os
import yaml
import json
import pandas as pd
import geopandas as gpd

DATABASEPATH = Path(os.path.realpath(__file__)).parent / 'database'
UNITYASSETPATH = Path(os.path.realpath(__file__)).parent.parent / 'unity' / 'GenAgentJune' / 'Assets'
UNITYANIMATIONPATH = UNITYASSETPATH / "Prefabs" / "Animations"
AGENTCONFIGPATH = Path(os.path.realpath(__file__)).parent.parent / 'configs' / 'agents'


class VerboseSafeDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def generate_tokenizer(cfg_environment, cfg_agents):
    """Generate a simple tokenizer that translate between int and str."""
    print('Generating tokenizer')
    print('environment config')
    print(cfg_environment)
    print('Agent config')
    print(cfg_agents)

    # Get building names from geoJSON file
    df = gpd.read_file(DATABASEPATH / f"{cfg_environment.name}_layout_copy.geojson")
    building_names = df['name'][df['feature_type'] == 'building'].tolist()

    file_path = AGENTCONFIGPATH / (cfg_agents.stories.name + '_gen_agents.yaml')
    stories = yaml.safe_load(open(file_path, 'r'))

    for name, details in stories['dict'].items():
        details['map'] = building_names

    with open(file_path, 'w') as yaml_file:
        yaml.dump(stories, yaml_file, Dumper=VerboseSafeDumper)

    file_path = DATABASEPATH / (cfg_agents.stories.name + '_gen_agents_copy.yaml')
    with open(file_path, 'w') as yaml_file:
        yaml.dump(stories, yaml_file, Dumper=VerboseSafeDumper)

    # Get agent names from demographics
    path = DATABASEPATH / (cfg_agents.demographics.name + '_demographics.csv')
    demographics_df = pd.read_csv(path)
    agent_names = list()
    for i in range(len(demographics_df)):
        name = demographics_df['First Name'][i].lower() + '_' + demographics_df['Last Name'][i].lower()
        agent_names.append(name)

    # Get all animation names from Unity folder
    animation_names = sorted([fn.stem for fn in UNITYANIMATIONPATH.glob('*.anim')])

    # Get all the names for tokenizer and make tokenizer
    all_names = building_names + agent_names + animation_names
    tokenizer_str2int = {name: i for i, name in enumerate(all_names)}
    tokenizer_int2str = {'items': all_names}

    # Save for both python and unity
    str2int_path = DATABASEPATH / f'{cfg_environment.name}_{cfg_agents.stories.name}_tokenizer_str2int.yaml'
    print('Saving tokenizer str2int', str2int_path)
    with open(str2int_path, 'w') as yaml_file:
        yaml.dump(tokenizer_str2int, yaml_file)



if __name__ == '__main__':
    pass
