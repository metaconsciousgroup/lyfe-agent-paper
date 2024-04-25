import os

from hydra import compose, initialize

configs_dir = os.path.dirname(os.path.abspath(__file__)) + "/configs"


def load_yaml_file(file_name):
    if not file_name.endswith(".yaml"):
        file_name += ".yaml"
    with initialize(version_base=None, config_path="configs"):
        cfg = compose(config_name=file_name)
    return cfg


supported_brain_cfgs = [
    "architect_brain",
    "base_brain",
    "find_person_brain",
    "freeze_at_start_brain",
]

brain_aliases = {
    "architect_brain": "architect_brain",
    "base_brain": "base_brain",
    "find_person_brain": "find_person_brain",
    "freeze_at_start_brain": "freeze_at_start_brain",
    "influence_brain": "base_brain",
    "personality_brain": "base_brain",
    "slow_brain": "base_brain",
    "slower_brain": "base_brain",
    "slowest_brain": "base_brain",
    "lively_brain": "base_brain",
}

brain_configs = {
    alias: load_yaml_file(brain_cfg_file_name)
    for alias, brain_cfg_file_name in brain_aliases.items()
}
