# Take in llm_response_data.json and sort the conversations
# Use graph structure

import hydra
import json
import pickle
import pandas as pd
from omegaconf import DictConfig, OmegaConf

from pathlib import Path


def load_chain_data(path):
    with open(path) as f:
        chain_data = json.load(f)
    return chain_data


def load_csv_as_pd(path):
    with open(path) as f:
        data = pd.read_csv(f)
    return data


@hydra.main(
    version_base=None, config_path="configs/data_process", config_name="data_process"
)
def main(cfg: DictConfig):
    dir = Path(cfg.data_dir)
    # Run beforehand (does any data preprocessing that you want)
    if hasattr(cfg, "run"):
        for key, value in cfg.run.items():
            if hasattr(value, "_partial_") and value._partial_:
                hydra.utils.instantiate(value)(dir)
            else:
                hydra.utils.instantiate(value)

    if cfg.process.get("save", None) is not None:
        save_dir = Path(cfg.process.save.name + "." + cfg.process.save.format)
        del cfg.process.save
    else:
        save_dir = None

    processed_data = hydra.utils.instantiate(cfg.process)
    
    # if save_dir:
    #     with open(dir / save_dir, "wb") as f:
    #         pickle.dump(processed_data, f)

###

    # print("RESULTS")
    # for key, value in processed_data.items():
    #     print(f"\n\n{key}:\n{value}")

    # # Save processed data
    # # TODO: temporary solution, pickle file is too large
    # with open(dir / "processed_data.pickle", "wb") as f:
    #     pickle.dump(processed_data, f)

    # # TODO: if we want to check occurrences in conversation, we need to load the pickle file
    # if cfg.check.occurrences:
    #     occurrence_result = hydra.utils.instantiate(cfg.check.occurrences)(
    #         dir / "processed_data.pickle"
    #     )

    # run_name = cfg.data_dir.split("/")[-1]

    # if cfg.check.in_memory:
    #     in_memory_result = hydra.utils.instantiate(cfg.check.in_memory)(
    #         dir / "0" / "agent_memory.json", occurrence_result
    #     )

    # if cfg.calculate.action_duration_time:
    #     average_durations = hydra.utils.instantiate(cfg.calculate.action_duration_time)(
    #         dir / "0" / "slow_forward_chain_data.json"
    #     )

    # result = {
    #     str(run_name): {"agent_info": in_memory_result}
    #     | {"action_average_durations": average_durations}
    # }
    # with open(dir / Path(run_name + "_occurrence_in_convo.json"), "w") as f:
    #     json.dump(result, f)


if __name__ == "__main__":
    main()
