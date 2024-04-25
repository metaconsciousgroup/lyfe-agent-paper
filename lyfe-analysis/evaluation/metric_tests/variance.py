import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(parent_dir)

import hydra
from lyfe_agent import create_agents
from utils.saveload import load_agent_data
from omegaconf import OmegaConf
from pathlib import Path

def metric_variance(cfg):
    """
    This function is used to calculate the variance of the metrics
    """
    path = Path(cfg.path) / str(cfg.get('run_num', 0))
    print(path)

@hydra.main(config_path='configs', config_name='obtain_info_test')
def main(cfg):
    cwdir = Path(cfg.path) / str(cfg.get('run_num', 0))

    # load original agent config
    agent_cfg_path = Path(dir / "0/.hydra/config.yaml")
    assert agent_cfg_path.exists(), "No agent config found."
    
    agent_cfg = OmegaConf.load(agent_cfg_path)
    original_agents_data = create_agents(agent_cfg, encoder_manager_enabled=True)


    agents = {agent.name: agent for agent in original_agents_data if agent.name in cfg.eval_multirun_agents}
    agents = load_agent_data(cwdir, agents)

    print("My agents: ", agents)

    for _ in range(cfg.num_trials):
        metric_variance(cfg)

if __name__ == '__main__':
    main()
