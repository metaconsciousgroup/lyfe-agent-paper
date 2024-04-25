import random

from typing import Dict, List, Optional, Tuple

from lyfe_agent.memory.memory_manager.skill_manager import SkillManager
from lyfe_agent.states.option_history import OptionHistory
from lyfe_agent.states.simple_states import CurrentOption, SimpleState
from lyfe_agent.states.timed_variables import OptionStatus

def get_enabled_abilities(abilities):
    abilities_list = [
        ability_name
        for ability_name, ability_config in abilities.items()
        if ability_config["enabled"]
    ]
    abilities_description = {key: abilities[key].description for key in abilities_list}

    return abilities_list, abilities_description

# TODO: Need to do some renaming given skill manager is now incorporated (e.g. all_available_options is not all available options)
class Options:
    """
    This class is responsible for managing the options that the agent's cognitive controller has access to.
    """
    def __init__(
        self,
        name: str,
        nearby_creature: SimpleState,
        observable_entities: SimpleState,
        current_option: CurrentOption,
        option_history: OptionHistory,
        skill_manager: SkillManager,
        abilities,
        prob_repeat=0.0,
        option_status=Dict,
    ):
        self.name = name
        self.nearby_creature = nearby_creature
        self.observable_entities = observable_entities
        self.current_option = current_option
        self.option_history = option_history
        self.skill_manager = skill_manager

        self.option_list, self.option_description = get_enabled_abilities(abilities)
        
        self._all_available_options = [
            opt
            for opt in self.option_list
            if not abilities.get(opt).get("root")
        ]

        self._available_options = self._all_available_options.copy()

        self.prob_repeat = prob_repeat
        self.last_chosen_option = None

        # Create Option Status
        self.option_status = OptionStatus(
            name=self.name,
            nearby_creature=self.nearby_creature,
            observable_entities=self.observable_entities,
            **option_status,
        )

        # determines the kinds of options that are available
        self.env_detail = None

        for item in self.option_list:
            self.option_status.add_variable(item)

    @property
    def data(self): # TODO: integrate with skill manager
        return self._available_options
    
    @property
    def illustration(self): # TODO: integrate with skill manager
        return "\n".join(
            f"{key}: {self.option_description[key]}"
            for key in self._available_options
            if key in self.option_description
        )
    
    def get_available_options_and_descriptions(self) -> Tuple[List[str], str]:
        """
        Returns a pair, where the first is a list of the available options
        and the second is a string containing the descriptions of the options.
        """
        # if not self.option_status.code_executing and self.env_detail != "basic":
        if self.env_detail != "basic":
            skills_buffer = self.skill_manager.get_buffer()
            skill_names = [skill["key"] for skill in skills_buffer]
            skill_desc_list = [skill["description"] for skill in skills_buffer]
            skill_desc = "".join([f"\n{name}: {desc}" for name, desc in zip(skill_names, skill_desc_list)])
        else:
            skill_names = []
            skill_desc = ""
        
        available_options = self.data + skill_names

        illustrations = self.illustration + skill_desc
        return available_options, illustrations

    @property
    def skill_set(self):
        return self.skill_manager.skill_set()

    # TODO: Renaming so that option list is some universal set of options and interview isn't special
    @property
    def option_set(self):
        return set(self.option_list + ["interview"] + list(self.skill_manager.skill_set()))

    def set_env_conditioning(self, env_detail: Optional[str]):
        """
        Takes details about the environment, specifying the types of options that are available.
        TODO: for now `env_detail` is a string, but really acts as a boolean
        where we only care if it is 'basic' or not 'basic'.
        """
        self.env_detail = env_detail

    def update(self, observations):
        self.option_status.update(observations)
        self.option_history.update(self.current_option)
        # Update skill manager if observation is interesting
        if observations.get("talk"):
            # Retrieve 3 possible skills
            # TODO: The retrieval is not working super well right now
            self.skill_manager.update_skill_buffer(observations["talk"], num_memories_retrieved=3)

        if not self.is_valid(self.current_option):
            # Not a valid action for this state
            return

        # set option restrictions based on the environment
        if observations.get("environment_details"):
            self.set_env_conditioning(observations["environment_details"])

        self._available_options = self._all_available_options.copy()

        self._update_last_chosen_option()

        # operations that modify the available options        
        self._possibly_avoid_action_repeat()
        self._talk_only_if_someone_is_around()

    def _update_last_chosen_option(self):
        if self.option_history.last_option and (
            self.option_history.last_option.option_name
            not in ["reflect", "cognitive_controller"]
        ):
            self.last_chosen_option = self.option_history.last_option.option_name

    # TODO: a patch to encourage agent to choose different actions
    def _possibly_avoid_action_repeat(self):
        if (
            self.last_chosen_option
            and self.last_chosen_option in self._available_options
            and not self.can_repeat()
        ):
            self._available_options.remove(self.last_chosen_option)

    def _talk_only_if_someone_is_around(self):
        if not self.nearby_creature.data and "talk" in self._available_options:
            self._available_options.remove("talk")

    def _attend_to_calendar(self, observations):
        # TODO: tool observation processing should be moved to a new inner observation interaction class
        if "tools" in observations and "calendar" in observations["tools"]:
            self._available_options = ["turn_off_alarm", "snooze_alarm"]
            return "alert"
        return "default"

    def can_repeat(self):
        if random.random() < self.prob_repeat:
            return True
        else:
            return False

    def is_valid(self, action):
        # Can consider whether we want to include passive states here
        return action.option_name in self.option_list
    
    # OPTION-STATUS RELATED METHODS
    def get_active_variables_list(self):
        return self.option_status.get_active_variables_list()
    
    # TODO: Right now this is too nested, need to refactor
    def modify_option(
        self, 
        option: str, 
        talk_obs: Optional[str] = None, 
        i_am_speaker: bool = False
    ) -> str:
        """
        Refines the option based on the current state of the agent.
        """
        return self.option_status.update_option(option, talk_obs, i_am_speaker)

    def activate_variable(self, name: str, lifespan: int = None):
        self.option_status.activate_variable(name, lifespan)