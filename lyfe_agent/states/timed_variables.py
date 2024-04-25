from typing import Dict, List, Optional

import logging
import time

from lyfe_agent.utils.space_utils import get_nearby_entities_action_info

logger = logging.getLogger(__name__)


class TimedVariable:
    def __init__(self, name, lifespan=1_000_000):
        self.name = name
        self.lifespan = lifespan
        self.remaining = 0

    def activate(self, lifespan=None):
        if lifespan is not None:
            self.lifespan = lifespan
        self.remaining = self.lifespan

    def deactivate(self):
        self.remaining = 0

    def update(self):
        if self.remaining > 0:
            self.remaining -= 1

    def is_active(self):
        return self.remaining > 0


class TimedVariables:
    """
    This class provides a mechanism to manage and track a collection of timed variables.
    A timed variable can be activated or deactivated and has a specified lifespan,
    after which it becomes inactive.
    Rules can be set for variables to specify other variables that should be deactivated
    when a particular variable is activated.
    """

    def __init__(self, rules: Dict[str, List[str]] = {}):
        self.variables: Dict[str, TimedVariable] = {}
        self.rules = dict(rules)
        self.time = 0

    def add_variable(self, name: str, lifespan: int = 1_000_000, timed_var=None):
        """Add a variable to the timed variables.

        Args:
            name (str): Name of the variable.
            lifespan (int, optional): Lifespan of the variable. Defaults to 1_000_000.
        """
        if name not in self.variables:
            if timed_var is None:
                self.variables[name] = TimedVariable(name, lifespan)
            else:
                self.variables[name] = timed_var
        else:
            logger.debug(f"Variable {name} already exists.")

    def set_rules(self, name: str, disables: List[str] = []):
        if name in self.variables:
            self.rules[name] = disables
        else:
            logger.debug(f"Variable {name} does not exist. Please add it first.")

    def activate_variable(self, name: str, lifespan: int = None):
        if name in self.variables.keys() and name != "cognitive_controller":
            if name in self.rules.keys():
                for var_name in self.rules[name]:
                    if var_name in self.variables.keys():
                        self.deactivate_variable(var_name)
                    else:
                        logger.debug(
                            f"Variable {var_name} to deactivate does not exist."
                        )
            self.variables[name].activate(lifespan)
        else:
            logger.debug(f"Variable {name} to activate does not exist.")

    def deactivate_variable(self, name: str):
        if name in self.variables:
            self.variables[name].deactivate()
        else:
            logger.debug(f"Variable {name} to deactivate does not exist.")

    def update(self):
        self.time += 1
        for name, var in self.variables.items():
            var.update()

    def print_status(self):
        logger.debug(f"Time: {self.time}")
        for name, var in self.variables.items():
            logger.debug(
                f'Variable {name}: {"Active" if var.is_active() else "Inactive"}'
            )

    def get_active_variables(self) -> str:
        return " ".join(
            [
                name
                for name, var in self.variables.items()
                if var.is_active() and name != "cognitive_controller"
            ]
        )

    def get_active_variables_list(self) -> List[str]:
        return [name for name, var in self.variables.items() if var.is_active()]

    def check_if_active(self, name: str) -> bool:
        if name in self.variables.keys():
            return self.variables[name].is_active()
        else:
            return False


class OptionStatus(TimedVariables):
    """Keeping track of the status of option execution."""

    def __init__(self, name, nearby_creature, observable_entities, rules={}):
        super().__init__(rules)
        self.name = name
        self.nearby_creature = nearby_creature
        self.observable_entities = observable_entities

        self._default_latency = 5
        self._next_latency = self._default_latency
        self._in_convo = False
        self._last_option = "cognitive_controller"  # initial
        # Bool to track when in talk state, but after talk obs produced
        self._i_am_speaking = False

        self.code_executing = False

        # variable setup
        variables = ["cognitive_controller", "talk", "wait", "listen"]
        # TODO: maybe move
        self.options = [
            "cognitive_controller",
            "talk",
            "wait",
            "listen",
            "message",
            "choose_destination",
            "reflect",
        ]
        for var in variables:
            self.add_variable(name=var)
            others = [other for other in variables if other != var]
            if var not in self.rules.keys():
                self.rules |= {var: others}
            else:
                self.rules[var] += others

    def latency(self, talk_obs, i_am_speaker):
        if i_am_speaker:
            return 1_000 * self._default_latency # the higher the multiplier, the longer before talking after you already spoke
        elif any([name_part in talk_obs for name_part in self.name.split()]):
            return 0
        else:
            return self._default_latency

    def handle_conversation(
        self, option: str, talk_obs: Optional[str], i_am_speaker: bool = False
    ):
        self._in_convo = True

        # Set latency if talk observation
        if talk_obs:
            self._next_latency = self.latency(talk_obs, i_am_speaker)
            if i_am_speaker:
                self._i_am_speaking = True

        # Enter convo logic
        if self._last_option not in ["talk", "listen", "wait"]:
            option = "talk" if self.able_to_talk else "listen"
            self.activate_variable(option, lifespan=1_000_000)

        elif self._last_option == "wait":
            if self.variables["wait"].is_active():
                option = "wait"
            else:
                option = "talk" if self.able_to_talk else "listen"
                self.activate_variable(
                    option, lifespan=1_000_000
                )  # talk and listen are initially indefinite

        elif self._last_option == "talk":
            if self.variables["talk"].is_active():
                option = "talk"
            else:
                option = "wait"
                self.activate_variable(option, lifespan=self._next_latency)
                self._i_am_speaking = False

        elif self._last_option == "listen":
            if not self.able_to_talk:
                option = "listen"
            else:
                option = "wait"
                self.activate_variable(option, lifespan=self._next_latency)
        self._last_option = option
        return option

    # TODO: Revisit
    def update(self, observations=None):
        super().update()
        if self._last_option == "talk" and not self.variables["talk"].is_active():
            pass
            # print(f"[{self.name}], {time.time()}: talk no longer active.")
        if observations is not None and observations.get("general"):
            if observations["general"] == "done":
                self.code_executing = False

    @property
    def able_to_talk(self):
        # able_to_talk = (
        #     True
        #     if "talk" not in get_nearby_entities_action_info(self.nearby_creature.data)
        #     else False
        # )
        if self.observable_entities.data is None:
            return False
        able_to_talk = all(["talk" not in actions for actions in self.observable_entities.data.values()])

        return able_to_talk

    def update_option(
            self, 
            option: str, 
            talk_obs: Optional[str] = None, 
            i_am_speaker: bool = False
    ) -> str:
        if option in ["talk", "listen", "wait"]:
            option = self.handle_conversation(option, talk_obs, i_am_speaker)
        # TODO: Temporary patch
        elif option not in self.options:
            self.code_executing = True
        else:
            self._in_convo = False
            self._last_option = option
            self.activate_variable(option)
        return option
