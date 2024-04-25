import datetime
import random

from lyfe_agent.states.options import Options
from typing import Dict, Optional

from lyfe_agent.states.simple_states import describe_location


# TODO: More structured description
AgentStateData = Dict

# Class that aggregates all agent states together that are passed downstream (container of states)
# Note that the current definition is a temporary one
class AgentState:
    """
    Container class for all the agent states.
    - Passed as input to chains
    - Can be queried for booleans regarding internal states
    """
    metadata = [
        "name",
        "personality",
        "current_goal",
        "knowledge",
        "evaluation_monitor",
        "schedule",
    ]

    def __init__(
        self,
        agent,
        options: Options,
        prob_boredom: float,
        suspended_time: float,
        **data
    ): # agent as input is temporary and only used for instantiation
        for key in self.metadata:
            setattr(self, key, getattr(agent, key))
        self.options = options
        self.prob_boredom = prob_boredom
        self.suspended_time = suspended_time
        self.always_run_slow = False # seems default behavior

        self.state_keys = data.keys()
        for key in self.state_keys:
            setattr(self, key, data[key])

        # self._data = {} if data is None else data  # Note the underscore prefix
        self._data = {}

        self.nonce = [None, '', ' ', '\n', '.']

        self.available_options = []
        self.skill_options = []

    def update(self, observations: Dict):
        """
        Where all state updates are gathered
        """
        self.current_time.update(observations.get("time"))
        self.nearby_creature.update(observations.get("nearby_creature"))
        self.contacts.update(observations.get("contacts"))
        self.observable_entities.update(observations.get("observable_entities"))
        self.knowledge.update(observations)
        # Evaluation is used for downstream tasks outside the simulation
        self.evaluation_monitor = observations.get("evaluation_monitor", False)

        self.schedule.update(new_time=self.current_time.data)
        self.options.update(observations)
        # self.option_history.update(self.current_option)
        self.repetition_detector.update()
        self.expiretime_detector.update(self.current_option)

    # Perceptions that are observable to the agent, passed along to chains
    @property
    def data(self) -> AgentStateData:
        self._data.update({
            "name": self.name, # this is the only one that is a string right now
            "personality": self.personality,
            "current_goal": self.current_goal,
            "current_time": self.current_time.data,
            "time": self.current_time.data,
            "map": self.knowledge.get_map_content(self.location),
            "receiver": "None",
            "bag_content": self.knowledge.get_bag_content(),
            "contacts": self.contacts.get_contacts(),
            "evaluation_monitor": self.evaluation_monitor,  # Used for downstream tasks outside the simulation
        })
        # get world model related information
        self._data |= self.summary_state.data
        self._data |= self.current_option.data

        # get location
        self._data["location"] = describe_location(self.location)

        self._data["nearby_creature"] = ", ".join(
            [str(n) for n in self.nearby_creature.data]
            if self.nearby_creature.data  # is not None
            else []
        )

        available_options, illustrations = self.options.get_available_options_and_descriptions()
        
        self._data["option_list"] = available_options
        self._data["illustration"] = illustrations

        self._data["realworld_datetime"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return self._data

    # Make updates related to action here
    def start_action(self, action):
        pass

    def end_action(self, action):
        pass

    # Booleans
    def should_submit_action_selection(self):
        # some special agents are not observing time_based new_events
        bored = (random.random() < self.prob_boredom)
        should_submit = self.new_event_detector.data or self.always_run_slow or bored
        summary_has_been_run = all(value not in self.nonce for value in self.summary_state.data.values())
        should_submit = should_submit and summary_has_been_run

        # NOTE: the check for summary_state ensures agents to have action_selection after getting first summary
        return should_submit

    # Method related to agent 'expression': those features which are observable by others
    @property
    def expressions(self):
        """
        Aspects of the agent that can be perceived by other agents
        """
        return {"expressions": self.options.get_active_variables_list()}
    

    # # Detector related methods
    def set_new_event(self, new_event: bool, source_reason: Optional[str] = None) -> None:
        self.new_event_detector.update(new_event, source_reason)

    # TODO: Will want to generalize this
    def exit_current_option(self):
        """Used to determine whether to exit to cognitive controller or reflection"""
        return self.repetition_detector.is_repetitive or self.expiretime_detector.is_expired

    # Retrieve information from agent state
    def get_time(self):
        return self.current_time.data
    
    # # OPTION RELATED METHODS
    def has_option(self, option_name: str) -> bool:
        """Does agent have this option?"""
        return option_name in self.options.option_set
    
    def has_skill(self, option_name: str) -> bool:
        """Does agent have this skill?"""
        return option_name in self.options.skill_set

    def get_current_option(self) -> str:
        return self.options.current_option.option_name

    def update_option(
            self,
            option_name: str,
            option_goal: str = None,
    ):
        if option_goal is None:
            option_goal = self.options.current_option.option_goal
        self.options.current_option.update(
            option_name=option_name,
            option_goal=option_goal,
        )

    # TODO: This is not well named
    def modify_option(
        self, 
        option: str, 
        talk_obs: Optional[str] = None, 
        i_am_speaker: bool = False
    ) -> str:
        """
        Refines the option based on the current state of the agent.
        """
        return self.options.modify_option(option, talk_obs, i_am_speaker)
    