import asyncio
import os
import hydra
from omegaconf import DictConfig, OmegaConf
from hydra.utils import instantiate 
from hydra.core.global_hydra import GlobalHydra
import json

from lyfe_agent.langmodel import get_api_keys
from utils.saveload import load_chain_data

# grab api keys
api_keys = {
    "openai": {"openai_api_key": get_api_keys()["openai"][0]}
}



class ChainManager:
    """
    This class manages the chains for a given brain configuration. Very stripped down implementation.
    Currently does not support querying for memories
    """

    def __init__(self, cfg) -> None:

        self.llm = instantiate(cfg.langmodel)()
        # collect dictionary of chains
        self.chains = {
            cfg_key: instantiate(cfg_val)(
                llm=self.llm,
                memory=None,
                name="Evaluation"
            )
            for cfg_key, cfg_val in cfg.chains.items()
        }

def load_config(config_path: str, config_name: str, overrides: list = []):
    GlobalHydra.instance().clear()
    hydra.initialize(config_path= config_path)
    cfg = hydra.compose(config_name=config_name, overrides=overrides)
    return cfg

def select_run():
    base_dir = "multirun"
    dates = sorted(
        [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    )

    print("Select a date:")
    for i, date in enumerate(dates):
        print(f"{i+1}: {date}")

    date_idx = int(input("Enter the number of the date: ")) - 1
    selected_date = dates[date_idx]

    runs_dir = os.path.join(base_dir, selected_date)
    runs = sorted(
        [d for d in os.listdir(runs_dir) if os.path.isdir(os.path.join(runs_dir, d))]
    )

    print("Select a run:")
    for i, run in enumerate(runs):
        print(f"{i+1}: {run}")

    run_idx = int(input("Enter the number of the run: ")) - 1
    selected_run = runs[run_idx]

    return os.path.join(base_dir, selected_date, selected_run)

# for printing all evaluation results
def print_score_table(evaluations, brain_names, data):
    # Define the headers
    headers = ["Evaluation"] + [f"{name} Score" for name in brain_names] + ["Number of Events"]

    # Print the headers
    print("|".join([f"{header:^20}" for header in headers]))

    # Print separator
    print("-" * (20 * len(headers) + len(headers) - 1))

    # Extract the required information and print
    for evaluation in evaluations:
        row = [evaluation]
        event_num_list = []
        for name in brain_names:
            percent = data[name][evaluation]['score'] * 100
            row.append(f"{percent:.2f}%")
            event_num_list.append(data[name][evaluation]['num_events'])
        event_num_list = set(event_num_list)
        assert len(set(event_num_list)) == 1, "Number of events is not the same across brains"
        row.append(event_num_list.pop())
        
        print("|".join([f"{cell:^20}" for cell in row]))

def brain_evaluation(cfg):
    # collect any llms that are used
    llms = {}
    for org, org_llms in cfg.llm.items():
        api_key_arg = api_keys[org]
        llms = {name: instantiate(llm)(**api_key_arg) for name, llm in org_llms.items()}

    # get and load configs for brains
    chain_managers = {}
    for brain_name, inputs in cfg.brain_cfgs.items():
        config = load_config(inputs.config_path, inputs.config_name)
        config = config if "key" not in inputs else config[inputs.key]
        chain_managers[brain_name] = ChainManager(config)
    brain_names = chain_managers.keys()

    # Load chain data
    chain_data = load_chain_data(cfg.simulation.config_path)

    # Print the available functions to evaluate
    print(chain_data.keys())

    # Run evaluations
    eval_results = {}
    for brain_name, chain_manager in chain_managers.items():
        eval_results[brain_name] = {}
        for eval_name, eval_cfg in cfg.evaluations.items():
            eval_cfg = eval_cfg.copy()
            if 'llm' in eval_cfg:
                llm = llms[eval_cfg.llm]
                OmegaConf.set_struct(eval_cfg, False)
                del eval_cfg.llm
            else:
                llm = None
            result = instantiate(eval_cfg)(
                llm=llm, 
                chain_data=chain_data,
                chain_manager=chain_manager
                )
            eval_results[brain_name][eval_name] = result
    print(eval_results)

    # Print scores:
    print_score_table(
        evaluations=cfg.evaluations.keys(),
        brain_names=brain_names,
        data=eval_results
        )

def get_last_element(input_string):
    """
    Retrieves the last element of a dot-separated string.
    
    Parameters:
    - input_string (str): The dot-separated string from which to extract the last element.
    
    Returns:
    str: The last element of the dot-separated string.
    
    Example:
    >>> get_last_element('something.something.something.hello')
    'hello'
    """
    parts = input_string.split('.')
    last_part = parts[-1]
    return last_part

def add_async_to_last_element(input_string):
    """
    Modifies the last element of a dot-separated string by prepending 'async_' to it.
    
    Parameters:
    - input_string (str): The dot-separated string to modify.
    
    Returns:
    str: A new string with 'async_' prepended to the last element.
    
    Example:
    >>> add_async_to_last_element('something.something.something.hello')
    'something.something.something.async_hello'
    """
    parts = input_string.split('.')
    last_part = parts[-1]
    parts[-1] = f'async_{last_part}'
    return '.'.join(parts)

async def async_brain_evaluation(cfg):
        # collect any llms that are used
    llms = {}
    for org, org_llms in cfg.llm.items():
        api_key_arg = api_keys[org]
        llms = {name: instantiate(llm)(**api_key_arg) for name, llm in org_llms.items()}

    # get and load configs for brains
    chain_managers = {}
    for brain_name, inputs in cfg.brain_cfgs.items():
        config = load_config(inputs.config_path, inputs.config_name)
        config = config if "key" not in inputs else config[inputs.key]
        chain_managers[brain_name] = ChainManager(config)
    brain_names = chain_managers.keys()

    # Load chain data
    chain_data = load_chain_data(cfg.simulation.config_path)

    # Print the available functions to evaluate
    print(chain_data.keys())

    # Run evaluations
    eval_results = {}
    tasks = []
    for brain_name, chain_manager in chain_managers.items():
        eval_results[brain_name] = {}
        for eval_name, eval_cfg in cfg.evaluations.items():
            eval_cfg = eval_cfg.copy()
            if 'llm' in eval_cfg:
                llm = llms[eval_cfg.llm]
                OmegaConf.set_struct(eval_cfg, False)
                del eval_cfg.llm
            else:
                llm = None
            # change target name if necessary
            if 'async' not in get_last_element(eval_cfg._target_):
                eval_cfg._target_ = add_async_to_last_element(eval_cfg._target_)
            task = instantiate(eval_cfg)(
                llm=llm, 
                chain_data=chain_data,
                chain_manager=chain_manager
                )
            tasks.append((brain_name, eval_name, task))
    
    # Run tasks in parallel
    results = await asyncio.gather(*(task for _, _, task in tasks))

    # Save results
    for (brain_name, eval_name, _), result in zip(tasks, results):
        eval_results[brain_name][eval_name] = result
    print(eval_results)

    # Print scores:
    print_score_table(
        evaluations=cfg.evaluations.keys(),
        brain_names=brain_names,
        data=eval_results
        )

@hydra.main(
    version_base=None, config_path="configs/evaluation/brain_eval", config_name="brain_eval"
)
def main(cfg: DictConfig):
    # # config_path = select_run()
    # # config_path = os.path.join(config_path,'0')

    # brain_evaluation(cfg)

    import time

    start = time.time()

    if cfg.get("async"):
        asyncio.run(async_brain_evaluation(cfg))
    else:
        brain_evaluation(cfg)

    print(time.time() - start)

    # # Get special events (this is prespecified in the config)
    # special_event_nums = list(cfg.simulation.special_events)

    # for i in special_event_nums:
    #     print("\nEVENT NUMBER: ", i)
    #     transition = chain_data['talk'][i]
    #     content = extract_recent_content(transition['input']['convomem'])
    #     print(content)
    #     response = transition['output']['response']
    #     print(response)






if __name__ == "__main__":
    main()


