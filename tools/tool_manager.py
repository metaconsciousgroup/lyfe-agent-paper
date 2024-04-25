from typing import Dict
from lyfe_agent.base import BaseInteraction
from tools.base import Tool

class ToolManager(BaseInteraction):
    """
    The tool manager is responsible for managing the tools that the agent has access to.
    For now the tool manager is another attribute that the agent has.
    At every agent iteration, we run
        1. `act` which takes the agent action and applies the appropriate effects on tools
        2. `execute` which updates the tool based on the observations
    We view this class as an `Interaction` because we can think of tool updates as potentially requiring LLM calls. 
    """
    def __init__(self, tools: Dict[str, Tool]):
        self.tools = tools

    def execute(self, observations, action):
        for tool in self.tools.keys():
            tool.update(observations)

    def act(self, action):
        """
        Agent action on tool
        """
        for tool, action_details in action["use_tool"]:
            getattr(tool, action_details["option_name"])(action_details["action_args"])
        # if we want this to influence the observation then we need it done on the `tool.update` step
        

