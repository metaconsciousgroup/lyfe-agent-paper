import warnings
import logging
import sys
import hydra
from omegaconf import DictConfig

from utils.run import run_agents
from utils.config_utils import (
    parse_config,
    expand_config_by_environment,
    expand_brain_configuration,
)
from lyfe_agent import get_env_vars
from pathlib import Path


warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)  # Configure root logger
# # Disable logging from faiss and sentence transformers --- still allow warnings
# logging.getLogger("faiss.loader").setLevel(logging.WARNING)
# logging.getLogger("sentence_transformers.SentenceTransformer").setLevel(logging.WARNING)


@hydra.main(version_base=None, config_path="configs", config_name="demo")
def main(cfg: DictConfig):
    expanded_cfg = expand_config_by_environment(cfg)
    expanded_cfg = expand_brain_configuration(expanded_cfg)
    parse_config(expanded_cfg)

    base_dir = Path(__file__).resolve().parent
    env_file_path = base_dir / ".env"
    env_dict = get_env_vars(env_file_path=env_file_path)
    run_agents(expanded_cfg, env_dict)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.exit(e)
