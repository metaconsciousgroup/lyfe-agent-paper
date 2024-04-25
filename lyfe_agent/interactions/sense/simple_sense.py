"""Sense functions of the agent."""

from lyfe_agent.base import BaseInteraction
from lyfe_agent.brain_utils import RecentInputs
from lyfe_agent.states.simple_states import describe_location


def process_time(self, observations, sense_natural_language):
    if observations.get("time"):
        sense_natural_language["time"] = observations["time"]
        self.recent_time_input.add_content(observations["time"])
    return False


def process_arrival(self, observations, sense_natural_language):
    if observations.get("move_ended", None):
        # self.agent.location = Location(True, observations.get("move_ended", None))
        loc_type = (
            "place" if self.location.destination in self.knowledge.map else "person"
        )
        self.location.update(
            True, observations.get("move_ended", None), loc_type, self.nearby_creature
        )
        sense_natural_language["choose_destination"] = "I am " + describe_location(
            self.location
        )
        return True
    return False


def process_communication(self, observations, sense_natural_language):
    new_event = False
    for key in ["message", "talk", "interview"]:
        obs_value = observations.get(key)
        if obs_value is not None and obs_value not in self.recent_event_input:
            sense_natural_language[key] = obs_value
            self.recent_event_input.add_content(obs_value)
            new_event = True
            # if key == "talk" and new_event:
            #     agent._was_talked_to = True
    return new_event


def process_vision(self, observations, sense_natural_language):
    if (
        observations.get("visible_creatures") is not None
        and observations["visible_creatures"] not in self.recent_vision_input
    ):
        agent_names = observations["visible_creatures"]

        if len(agent_names) > 0:
            creatures_list = sorted(agent_names)  # Convert to sorted list for consistent order
            creatures_text = ', '.join(creatures_list)  # Join elements into a string
            vision_text = f"I see {creatures_text}".strip()
            sense_natural_language["vision"] = vision_text
        self.recent_vision_input.add_content(observations["visible_creatures"])
    return False

def process_feedback(self, observations, sense_natural_language):
    feedback = observations.get("general")
    if feedback is not None:
        sense_natural_language["general"] = feedback
        return True

# def process_inner_observation(self, inner_observation, sense_natural_language):
#     if inner_observation is not None:
#         sense_natural_language["inner_status"] = inner_observation
#         return True
#     return False


# TODO: make target not None
class SenseInteraction(BaseInteraction):
    expected_inputs = [
        "name",
        "location",
        "knowledge",
        "nearby_creature",
        "new_event_detector",
        "encoders",
    ]

    def __init__(self, sources, targets, encoder_key="openai", **kwargs):
        super().__init__(sources, targets)
        self.recent_vision_input = RecentInputs()
        self.recent_time_input = RecentInputs()
        self.recent_event_input = RecentInputs(max_size=100)

        self.encoder = self.encoders.models[encoder_key]

    def execute(self, observations):
        """
        :return: An input_to_state that consists of
        - a natural language summary of the observation
        - a boolean indicating whether a new event has occurred
        """
        sense_natural_language = {}
        new_event = any(
            [
                process_time(self, observations, sense_natural_language),
                process_arrival(self, observations, sense_natural_language),
                process_communication(self, observations, sense_natural_language),
                process_vision(self, observations, sense_natural_language),
                process_feedback(self, observations, sense_natural_language),
                # process_inner_observation(self, None, sense_natural_language),
            ]
        )

        # THIS IS TEMPORARY (UPDATES SHOULDN'T OCCUR INSIDE INTERACTIONS)
        if self.new_event_detector.data or new_event:
            source_reason = "new event"
            if self.new_event_detector.data and new_event:
                source_reason = "new event combined with previous event"
            elif self.new_event_detector.data:
                source_reason = "previous event left"

            self.new_event_detector.update(
                new_event=(new_event or self.new_event_detector.data),
                source_reason=source_reason,
            )

        self.event_tracker.receive(new_event)

        return sense_natural_language
