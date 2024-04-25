import logging
import json
import time
import os
from pathlib import Path
from omegaconf import OmegaConf

from lyfe_bench.environments.testbed_env.testbed_env import GraphEnv
from lyfe_bench.evaluation.interview import interview, judge_response, extract_content
from lyfe_bench.evaluation.check_location import check_location
from lyfe_bench.evaluation.utils.evaluation_log_utils import post_process

logger = logging.getLogger(__name__)

def all_equal_and_not_none(x):
    if not x or x[0] is None:
        return False
    return all(element == x[0] for element in x)

def apply_func_from_name(func_name: str, arg):
    """
    Given function identifier `func_name` and args, output the function on those args
    """
    func_names = {"all": all, "any": any, "all_equal_and_not_none": all_equal_and_not_none, "not": lambda x: not x[0]}
    assert func_name in func_names, f"Function name {func_name} not found in {func_names}"
    func = func_names[func_name]
    return func(arg)


class BenchmarkEnv(GraphEnv):
    """Wrapper allowing for postprocessing after environment close.
    
    TODO: Need to be substantially overhauled. The structure doesn't make sense right now
    Env shouldn't be responsible for post processing.

    Better solution is probably to have functions that run benchmarking
    allowing benchmarking to be run not just in the environment but also in other contexts.
    """

    def __init__(self, agents_dict, specs, evaluators_dict=None, **kwargs):
        # Specs
        self.agents_specs = specs["agents"]
        self.env_specs = specs["env"]
        self.eval_specs = specs["evaluation"]
        self.save_dir = Path(kwargs.get("save_dir", None))
        # Agent related information
        self.agents_dict = agents_dict
        agents = [a.name for a in agents_dict.values()]
        
        # Dictionary of evaluators
        self.evaluators_dict = evaluators_dict

        # Time tracking
        self.sim_start = time.perf_counter()
        self.total_time = self.env_specs["total_time"]
        del self.env_specs["total_time"]

        super().__init__(agents, **self.env_specs)


    def time_update(self):
        super().time_update()
        self.sim_time = time.perf_counter() - self.sim_start
        if self.sim_time > self.total_time:
            return True
        return False

    def run_evaluation_item(self, eval_item, output_vars):
        if eval_item["method"] == "judge_interview":
            self.run_judge_interview(eval_item, output_vars)
        if eval_item["method"] == "extract_interview":
            self.run_extract_interview(eval_item, output_vars)
        elif eval_item["method"] == "success":
            self.run_success(eval_item, output_vars)
        elif eval_item["method"] == "check_location":
            self.run_check_location(eval_item, output_vars)

    def run_judge_interview(self, eval_item, output_vars):
        """
        Evaluates a judge_interview item.
        A judge_interview item consists of:
        - An agent specified, to be interviewed
        - A question to be asked
        - The answer that is expected
        Modifies the evaluation output by adding
        - `interview_response`: which takes the output from the agent's interview
        - `output`: which takes the output from the judge's evaluation of `interview_response`
        """
        agent = self.agents_dict[eval_item["agent"]]
        question = eval_item["question"]
        answer = eval_item["answer"]

        response = interview(agent=agent, question=question)
        eval_item["interview_response"] = response

        # the judge is an object that must be supplied via the evaluators_dict
        judge = self.evaluators_dict["judge"]
        result = judge_response(question, answer, response, judge)

        output_vars.append(result)
        eval_item["output"] = result

    def run_extract_interview(self, eval_item, output_vars):
        agent = self.agents_dict[eval_item["agent"]]
        question = eval_item["question"]
        template = eval_item["template"]
        format = OmegaConf.to_container(eval_item["format"])

        response = interview(agent=agent, question=question)
        eval_item["interview_response"] = response

        extractor = self.evaluators_dict["extractor"]
        content = extract_content(question, response, template, format, extractor)

        output_vars.append(content)
        eval_item["output"] = content


    def run_check_location(self, eval_item, output_vars):
        agents = [self.agents_dict[agent] for agent in eval_item["agents"]]
        location = eval_item["location"]
        start_time = eval_item["start_time"]
        end_time = eval_item["end_time"]
        # Uses location_system history to check agent locations
        entities_present = check_location(
            history=self.location_system.history,
            agents=agents,
            location=location,
            start_time=start_time,
            end_time=end_time,
        )
        # record which entities were present at location
        eval_item["entities_present"] = entities_present

        result = set(entities_present) == set(agents)

        output_vars.append(result)
        eval_item["output"] = result

    def run_success(self, eval_item, output_vars):
        func_name = eval_item["func"]
        args_indices = eval_item["args"]
        args = [output_vars[idx] for idx in args_indices]
        success = apply_func_from_name(func_name, args)
        output_vars.append(success)
        eval_item["output"] = success

    def close(self):
        """
        Runs evaluations and saves them to a json file.
        """

        #Process the conversation
        if not os.path.isfile((self.save_dir) / "main_log.csv"):
            post_process(self.save_dir)    
    
        output_vars = []
        for eval_item in self.eval_specs:
            self.run_evaluation_item(eval_item, output_vars)

        # save output in json format
        results = OmegaConf.to_container(self.eval_specs)
        with open("results.json", "w") as f:
            json.dump(results, f, indent=4)

        print(self.world_time)

        # TODO: ensure interview in agent works

if __name__ == "__main__":
    pass