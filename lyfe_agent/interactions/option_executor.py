from collections import defaultdict
from typing import Any, Callable, Dict

from langchain_community.callbacks import get_openai_callback
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from lyfe_agent.base import BaseInteraction
from lyfe_agent.utils.name_utils import name_match, name_include
from lyfe_agent.states.agent_state import AgentStateData
from lyfe_agent.states.simple_states import CurrentOption, Location, SimpleState
from lyfe_agent.states.summary_state import SummaryState
from lyfe_agent.utils.code_utils import decorate_code

class BaseOptionExecutor(BaseInteraction):
    expected_inputs = []

    def __init__(
        self,
        memory_template: Dict = None,
        **kwargs,
    ):
        super().__init__(
            sources=kwargs.pop("sources", {}), targets=kwargs.pop("targets", None)
        )
        # Common attributes for all desires
        self.action_to_env = defaultdict(lambda: None)
        self.memory_input = defaultdict(lambda: None)
        self.module_name = None

        # To add necessary prefix/postfix to memory item
        # TODO: make it configurable later
        self.memory_templates = {
            # "plan": "Set my plan to: {response}",
            "goal": "Set my goal to: {response}",
            "talk": "I said: {response}",
            "message": "I messaged {receiver}: {response}",
            "choose_destination": "I decide to go to {response}",
            "find_person": "I decide to find {response}",
            # "reflect": "My reflection is: {response}",
            "reflect": "{response}",
        }

        # NOTE: probably will need later, to update option_list
        self.is_available = True
        self.is_active = False

    def execute(self, observations, agent_state_data: AgentStateData):
        """
        Execute the main logic for this desire.
        To be overridden by subclasses.

        Returns:
            action_to_env: Actions to be performed in the environment.
            memory_input: Input to be stored in memory.
        """
        raise NotImplementedError("Subclasses must implement this!")

    def run_llm(self, option: str):
        chain_answer, cb_info = self.llm_call(
            option=option,
            data_collector=self.data_collectors["slow_forward"],
        )

        # TODO: call directly an agent state method
        self.agent_state.options.activate_variable(
            option,
            cb_info["lifespan"],
        )

        return chain_answer

    def update_memory_input(self, chain_answer):
        if self.module_name in self.memory_templates:
            self.memory_input.update(
                {
                    self.module_name: self.memory_templates[self.module_name].format(
                        **chain_answer
                    )
                }
            )


class CognitiveControl(BaseOptionExecutor):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name

    def new_execute(self, observations, agent_state_data: AgentStateData):
        pass

    def execute(self, observations, agent_state_data: AgentStateData):
        self.is_active = True

        chain_answer = self.run_llm(self.module_name)

        if chain_answer and all(chain_answer):
            if self.agent_state.has_option(chain_answer["option_name"]):
                self.agent_state.update_option(**chain_answer)
                self.agent_state.set_new_event(
                    True, "cognitive_controller trigger"
                )  # The cognitive_controller itself is a new event
                self.action_to_env[self.module_name] = chain_answer["option_name"]
                self.update_memory_input(chain_answer)
            else:
                chain_answer["response"] = None
        self.is_active = False
        return self.action_to_env, self.memory_input


class Talk(BaseOptionExecutor):
    def __init__(self, name, talk_sensitive_keywords, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name
        self.talk_sensitive_keywords = talk_sensitive_keywords

    def execute(self, observations, agent_state_data: AgentStateData):
        if self.terminate():
            pass  # TODO: need to consider the logic here
            return self.action_to_env, self.memory_input

        self.is_active = True
        chain_answer = self.run_llm(self.module_name)

        if chain_answer and all(chain_answer):
            # TODO: a patch to make agent silent
            if "[NONE]" in chain_answer["response"].upper():
                chain_answer["response"] = None
            # TODO: a patch to make agent move
            else:
                is_included, chain_answer["response"] = name_include(
                    chain_answer["response"],
                    self.talk_sensitive_keywords,
                )
                if is_included:
                    self.agent_state.update_option(
                        option_name="choose_destination",
                        option_goal=f"Based on what I said '{chain_answer['response']}', I need to go somewhere.",
                    )
                    # TODO: do we want interaction to update any state within itself? - Ivy
                    self.agent_state.set_new_event(True)
                    self.event_tracker.receive(True)
            self.action_to_env[self.module_name] = chain_answer["response"]
            self.update_memory_input(chain_answer)
        self.is_active = False
        return self.action_to_env, self.memory_input

    def run_llm(self, option: str):
        chain_answer, cb_info = self.llm_call(
            option=option,
            data_collector=self.data_collectors["slow_forward"],
        )

        if option == "talk":
            self.agent_state.modify_option(
                option=option,
                talk_obs=chain_answer["response"],
                i_am_speaker=True,
            )

        # TODO: Call directly an agent state method
        self.agent_state.options.activate_variable(
            option,
            cb_info["lifespan"],
        )

        return chain_answer

    def terminate(self):
        # repetition-based / time-based checking
        should_terminated = self.agent_state.exit_current_option()
        has_reflect_available = self.agent_state.has_option("reflect")

        if should_terminated:
            if has_reflect_available:
                self.agent_state.update_option(option_name="reflect")
            else:
                self.agent_state.update_option(
                    option_name="cognitive_controller",
                    option_goal=None,
                )
            self.agent_state.set_new_event(
                True, "repetition_detector/expiretime_detector trigger"
            )
            self.is_active = False

        return should_terminated

# TODO: Remove. I don't think we are using this anymore
# class NewTalk(BaseOptionExecutor):
#     def __init__(self, name, action_sequence, talk_sensitive_keywords, **kwargs):
#         super().__init__(**kwargs)
#         self.module_name = name
#         self.option_action_sequence = action_sequence + ["exit"]
#         self.todo_action_sequence = self.option_action_sequence.copy()

#         self.talk_sensitive_keywords = talk_sensitive_keywords

#         assert id(self.todo_action_sequence) != id(
#             self.option_action_sequence
#         ), "Copy failed!"

#     def execute(self, observations, agent_state_data: AgentStateData):
#         pass

#     def terminate(self):
#         pass


class ChooseDestination(BaseOptionExecutor):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name

    def execute(self, observations, agent_state_data: AgentStateData):
        self.is_active = True
        chain_answer = self.run_llm(self.module_name)
        
        if chain_answer and all(chain_answer):
            is_match, chain_answer["response"] = name_match(
                chain_answer["response"], self.knowledge.map
            )
            if is_match:
                if self.location.destination != chain_answer["response"]:
                    self.location.update(False, chain_answer["response"])
                self.action_to_env[self.module_name] = chain_answer["response"]
                self.agent_state.update_option(
                    option_name="cognitive_controller",
                    option_goal=None,
                )
                self.update_memory_input(chain_answer)
        self.is_active = False
        return self.action_to_env, self.memory_input


class Message(BaseOptionExecutor):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name

    def execute(self, observations, agent_state_data: AgentStateData):
        self.is_active = True
        chain_answer = self.run_llm(self.module_name)

        if chain_answer and all(chain_answer):
            is_match, chain_answer["receiver"] = self.contacts.get_match(
                chain_answer["receiver"]
            )
            if is_match:
                self.action_to_env[self.module_name] = (
                    chain_answer["response"],
                    chain_answer["receiver"],
                )
                self.update_memory_input(chain_answer)
        self.is_active = False
        return self.action_to_env, self.memory_input


class Reflect(BaseOptionExecutor):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name

    def execute(self, observations, agent_state_data: AgentStateData):
        self.is_active = True
        chain_answer = self.run_llm(self.module_name)

        if chain_answer and all(chain_answer):
            self.agent_state.update_option(
                option_name="cognitive_controller",
                option_goal=None,
            )
            self.agent_state.set_new_event(True, "reflect trigger")
            self.event_tracker.receive(True)
            self.action_to_env[self.module_name] = chain_answer["response"]
            self.update_memory_input(chain_answer)
        self.is_active = False
        return self.action_to_env, self.memory_input


class FindPerson(BaseOptionExecutor):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name

    def execute(self, observations, agent_state_data: AgentStateData):
        self.is_active = True
        chain_answer = self.run_llm(self.module_name)

        if chain_answer and all(chain_answer):
            is_match, chain_answer["response"] = self.contacts.get_match(
                chain_answer["response"]
            )
            if is_match:
                if self.location.destination != chain_answer["response"]:
                    self.location.update(
                        False,
                        chain_answer["response"],
                        type="person",
                        nearby_creature=self.nearby_creature,
                    )
                # a hacky solution
                # TODO: this is not straightforward - only keyword `choose_destination` could make unity entity move.
                self.action_to_env["choose_destination"] = chain_answer["response"]
                self.action_to_env[self.module_name] = chain_answer["response"]
                self.agent_state.update_option(
                    option_name="cognitive_controller",
                    option_goal=None,
                )
                self.update_memory_input(chain_answer)
        self.is_active = False
        return self.action_to_env, self.memory_input


class Plan(BaseOptionExecutor):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name

    def execute(self, observations, agent_state_data: AgentStateData):
        self.is_active = True
        chain_answer = self.run_llm(self.module_name)

        if chain_answer and all(chain_answer):
            self.schedule.add_event_from_list(
                [event for event in chain_answer.values()]
            )
            self.action_to_env[self.module_name] = chain_answer["response"]
            self.update_memory_input(chain_answer)
        self.is_active = False
        return self.action_to_env, self.memory_input


class Infer(BaseOptionExecutor):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name

    def execute(self, observations, agent_state_data: AgentStateData):
        raise NotImplementedError("Infer is not implemented yet!")
        return self.action_to_env, self.memory_input


# # Link to tools
# class UseTool(BaseOptionExecutor):
#     def __init__(self, name, **kwargs):
#         super().__init__(**kwargs)
#         self.module_name = name

#     # SOMEHOW NEED TO COMMUNICATE WHAT EXACTLY COG CONTROLLER CHOSE
#     def execute(self, observations, agent_state_data: AgentStateData):
#         self.is_active = True
#         chain_answer = self.run_llm()

#         if chain_answer and all(chain_answer):
#             pass
#         self.is_active = False
#         return self.action_to_env, self.memory_input


class Interview(BaseOptionExecutor):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name
        # interview action maintains a summary state specifically for interviews
        self.summary_state = None
        self.interview_goal = "answer the interviewer's questions as best as I can"
        self.interview_location = Location(arrival=True, destination="interview area")
        self.interviewer_name = "the interviewer"
        self.interviewer_nearby_creature = SimpleState(data=[self.interviewer_name])
        self.interview_current_option = CurrentOption(
            option_name="interview", option_goal=self.interview_goal
        )

    def execute(self, observations, agent_state_data: AgentStateData):
        self.is_active = True
        # temporarily modify chain_input
        og_goal = self.llm_call.agent_state.current_goal
        og_location = self.llm_call.agent_state.location
        og_nearby_creature = self.llm_call.agent_state.nearby_creature
        og_current_option = self.llm_call.agent_state.current_option
        og_summary = self.llm_call.agent_state.summary_state

        self.llm_call.agent_state.current_goal = self.interview_goal
        self.llm_call.agent_state.location = self.interview_location
        self.llm_call.agent_state.nearby_creature = self.interviewer_nearby_creature
        self.llm_call.agent_state.current_option = self.interview_current_option

        # initialize summary here
        if self.summary_state is None:
            self.llm_call.agent_state._data["initial_question"] = observations[
                "interview"
            ]
            chain_answer, _ = self.llm_call(
                option="initialize_interview",
            )
            del self.llm_call.agent_state._data["initial_question"]
            self.summary_state = SummaryState(keys=chain_answer.keys())
            self.summary_state.update(**chain_answer)
        else:
            chain_answer, _ = self.llm_call(
                option="update_world_model",
            )
            self.summary_state.update(**chain_answer)
        # replace llm_call summary state
        self.llm_call.agent_state.summary_state = self.summary_state

        chain_answer, _ = self.llm_call(
            option="talk",
            data_collector=self.data_collectors["slow_forward"],
        )

        if chain_answer and all(chain_answer):
            # TODO: a patch to make agent silent
            if "[NONE]" in chain_answer["response"].upper():
                chain_answer["response"] = None
            self.action_to_env[self.module_name] = chain_answer["response"]
            self.update_memory_input(chain_answer)

        self.is_active = False
        # restore chain_input changes
        self.llm_call.agent_state.current_goal = og_goal
        self.llm_call.agent_state.location = og_location
        self.llm_call.agent_state.nearby_creature = og_nearby_creature
        self.llm_call.agent_state.current_option = og_current_option
        self.llm_call.agent_state.summary_state = og_summary

        return self.action_to_env, self.memory_input

    def update_memory_input(self, chain_answer):
        self.memory_input.update(
            {"interview": self.memory_templates["talk"].format(**chain_answer)}
        )


template = """
You are currently in Minecraft and chose to execute the following function: {func_name}
Here are docstrings for that function: {docstring}
You chose to run this function with the goal: '{option_goal}'
Note that the function is in javascript. 
Pick values for the variables for this function and return in the format:
`<function name here>(bot, <insert variables here>)`
Do not write anything beyond the output format suggested above.
"""
prompt = PromptTemplate.from_template(template)

class CodeOptionExecutor(BaseOptionExecutor):
    def __init__(self, name, description, docstring, code, llm, **kwargs):
        super().__init__(**kwargs)
        self.module_name = name
        self.description = description
        self.docstring = docstring
        self.code = code
 
        self.chain = LLMChain(prompt=prompt, llm=llm, verbose=True)
 
    def execute(self, observations, agent_state_data: AgentStateData):
        self.is_active = True

        self.action_to_env["code"] = self.code

        # THIS PART CORRESPONDS TO run_llm
        chain_input = {
            "func_name": self.module_name,
            "description": self.description,
            "docstring": self.docstring,
        }
        with get_openai_callback() as cb:
            chain_answer = self.chain.invoke(agent_state_data | chain_input)["text"]
            # token usage information
            cb_info = cb.__dict__
        
        # The command to be executed
        command = chain_answer

        # Provide both the code and the command to execute the code
        # Language specific decoration of the code
        command = decorate_code(command, "javascript")

        self.action_to_env["code"] = self.action_to_env["code"] + "\n\n" + command
        # NOTE THAT THERE IS NO ACTIVATION OF VARIABLE HERE

        self.agent_state.update_option(
            option_name="cognitive_controller",
            option_goal="",
        )
        
        self.agent_state.modify_option(option=self.module_name)

        mem_item = {"code": f"executing code for {self.module_name}"}
        self.memory_input.update(mem_item)

        self.is_active = False
        return self.action_to_env, self.memory_input