from hydra.utils import instantiate
from omegaconf import DictConfig
from typing import Optional

def create_evaluators(evaluators_cfg: Optional[DictConfig]):
    """
    
    """
    if evaluators_cfg is None:
        return {}
    evaluators_dict = {}
    for evaluator_name, evaluator_cfg in evaluators_cfg.items():
        evaluators_dict[evaluator_name] = instantiate(evaluator_cfg)
    return evaluators_dict

