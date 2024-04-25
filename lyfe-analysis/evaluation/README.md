# Evaluation Framework Readme

This readme provides an overview of the `evaluate.py` script, which is designed to be a modular and flexible framework for evaluating the multirun environments and agents within it across various metrics.

The main principle behind this script is the decoupling of evaluation metrics from the evaluation framework. New evaluation functions can be written independently and then easily integrated into the framework through the Hydra configuration system. This enables the script to be highly adaptable and extensible, accommodating different project requirements and expanding with new evaluation methods over time.

## Structure

The script currently consists of several functions that can be used to interact with your own metric functions:

1. `eval_multirun_agents()` -- used for multirun analysis (ie. summarizes across all runs)
2. `eval_multirun_logs()` --used for multirun analysis (ie. summarizes across all runs)
3. `eval_run()` --used for single run analysis (ie. generated metrics specific to 1 run)
4. `main()`
5. `select_run()`

### `eval_multirun_agents(cfg, agents, eval_dict) -> Dict[str, Any]`

The kwargs this function passes are `llm`, `results_dict`, and `agent`.

This function can be used to record metrics across multiple runs.  The purpose of it is to initialize a function that will interact with specific agents in some way, such as interviewing them. The metrics are stored in an evaluation dictionary in the format 

{"Agent_1" : {    "metric_1_name" : {...}, "metric_2_name" : {...}, ...   },

 "Agent_2" : {    "metric_1_name" : {...}, "metric_2_name" : {...}, ...  },
 
 ...
}

Currently implemented:

`check_response` - interviews the agent and uses a language model instance to check whether their response matches the information presented in the Hydra configuration

`check_memory` -  Retrieves the agent memories directly and uses a language model instance to check whether their response matches the information presented in the Hydra configuration

Use this function for any metric that requires you to interact with *specific* agents. Will run the specified functions for each provided agent, and generate a new entry in the evaluation dictionary that stores the metrics. The results are incremented for each run.

### `eval_multirun_logs(cfg, cwdir, eval_dict) -> Dict[str, Any]`

The kwargs this function passes are `llm`, `results_dict`, and `cwdir`.

This function can be used to record metrics across multiple runs. It is more general purpose, and will initialize a function that only requires the run path. It is useful when interacting with the logs of a run (as an example). The metrics are stored in an evaluation dictionary in the format 

{"metric_1_name" : {...} ,"metric_2_name" : {...}, ...}

Currently implemented:

`check_for_mention` - parses the log file and checks whether relevant information was mentioned in the log file. It retrieves a language model instance and uses it to compare the information in the log file with the information given in the Hydra configuration.

`check_for_repetition` - parses the log file and analyzes each agents messages separately. Given a buffer size, it will check whether consecutive messages by an agent have some repeated elements. it uses a language model instance to check for this repetition.

Use this function for more general metrics that only require files that exist within a specific run directory. The results are stored in the evaluation directory and incremented for each run.

### `eval_run(cfg, cwdir)`

The kwargs this function passes are `path`.

This function evaluates each run and generates plots according to the evaluation function specified in the Hydra configuration.

Currently implemented:

`temporal_analysis` - Plots the events of the run over time.

`conversation_analysis` - Processes agents' messages using various transformer models and plots results.

`agent_memory_analysis` - Analyzes similarity behind a specific agent's memory components in the embedding space

### `main(cfg)`

This is the main function of the script. It loads the agent data and performs evaluations as specified in the Hydra configuration. It maintains two dictionaries `eval_multirun_agents_dict` and `eval_multirun_logs_dict` to track performance across all runs. 

### `select_run()`

This function provides a way to select a specific run for evaluation interactively from the terminal.

## Usage

To run this script, execute:

```bash
python evaluate.py --config-name configs/evaluation/<your_configs>.yaml
```

You'll be prompted to select a run date and then a specific run for evaluation.

The behavior of the script is largely determined by the Hydra configuration. 

Here is an example of a configuration file `obtain_info_eval.yaml`:

```yaml
path: multirun/2023-07-19/09-06-00
reset_path: true

post_process:
    _target_: evaluation.utils.evaluation_log_utils.post_process
    _partial_: true

eval_multirun_agents:
    "Francesco Bianchi":
        who_is_owner:
            _target_: evaluation.eval_multirun_agents.check_response.check_response
            _partial_: true
            question: "Do you know who the owner of the sushi restaurant is?"
            correct_answers: "Marta Rodriguez owns the sushi restaurant."
                
eval_multirun_logs:
    question_asked:
        _target_: evaluation.eval_multirun_logs.check_for_mention.check_for_mention
        _partial_: true
        agent_name: "Francesco Bianchi"
        info_to_mention: "Do you know who the owner of the sushi restaurant is?"
```

This configuration defines the path to the run to evaluate, whether to reset the path, a post-processing function to execute, and evaluation functions for agents and interactions. The `eval_multirun_agents` section is indexed by agent names and then by evaluation task names. The `eval_multirun_logs` section is indexed by interaction types.

## Adding New Evaluation Functions

### First, figure out if your evaluation function needs to interact with the agents (in which case you use `eval_multirun_agents()`) or if you need to interact with the other information from the run, such as the log file (in which case you use `eval_multirun_logs()`). Pay attention to the **kwargs that these functions pass in the script, as you will need to specify all other paremeters inside of the configuration script

New evaluation functions should be written independently of the main script and registered into the Hydra configuration. Functions are referenced in the Hydra configuration using the `_target_` key, which should point to the fully-qualified Python path of the function. If the function needs to be partially applied, set the `_partial_` key to `true`, and specify the function's static arguments in the configuration.

For example, to add a new function `check_response_variety` that resides in the file `evaluation.eval_multirun_agents.check_response_variety` with a question "Do you like sushi?", we would add this to our Hydra configuration under the `eval_multirun_agents` section:

```yaml
"Francesco Bianchi":
    do_you_like_sushi:
        _target_: evaluation.eval_multirun_agents.check_response_variety.check_response_variety
        _partial_: true
        question: "Do you like sushi?"
        correct_answers: ["Yes, I do.", "Absolutely, I love sushi."]
```

Always use **kwargs when writing your function signature. this will ensure the functions can work seamlessly with the evaluation script.

## Concluding Notes

This script provides a modular and adaptable framework for evaluating agents and language models. It allows for new evaluation functions to be added flexibly using the Hydra configuration system, and supports a wide variety of evaluation tasks.

## Additional Remarks

Being familiar with Hydra configurations and **kwargs in python are essential in interacting with the evaluation pipeline. 