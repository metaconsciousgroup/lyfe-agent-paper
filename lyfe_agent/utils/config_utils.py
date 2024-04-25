import logging
from omegaconf import DictConfig, OmegaConf
from typing import List

logger = logging.getLogger(__name__)


def process_config_for_instantiate(cfg: DictConfig, inputs_keys: List[str]):
    """
    Processes the given OmegaConf configuration for instantiation.

    Args:
        cfg: The input configuration to be processed.
        inputs_keys: List of keys to extract arguments from within the configuration.

    Returns:
        tuple: A tuple containing the modified configuration and a dictionary mapping from
               the input keys to their corresponding arguments.

    Note:
        The function makes a copy of the provided configuration, sets its structure
        to False to allow modifications, extracts arguments for the specified input keys,
        and marks the config for partial updates by setting `_partial_` to True.
    """
    cfg = cfg.copy()
    OmegaConf.set_struct(cfg, False)
    args_dict = {}
    for key in inputs_keys:
        if hasattr(cfg, key):
            args = list(cfg[key])
            del cfg[key]
        else:
            args = []
        args_dict[key] = args
    # instantiate state
    cfg._partial_ = True
    return cfg, args_dict