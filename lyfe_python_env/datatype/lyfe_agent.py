from typing import List
from pydantic import BaseModel, root_validator


# class LyfeAgent(BaseModel):

#     def __init__(self, agent_str):
#         fields: List[str] = agent_str.split("?")
#         self.agent_id = fields[0]
#         self.team = fields[1]
#         self.brain_id = fields[2]

class LyfeAgent(BaseModel):
    agent_id: str
    team: str
    brain_id: str

    @root_validator(pre=True)
    def extract_fields(cls, values):
        agent_str = values.get('agent_str')
        if agent_str:
            fields = agent_str.split("?")
            if len(fields) == 3:
                values['agent_id'] = fields[0]
                values['team'] = fields[1]
                values['brain_id'] = fields[2]
            else:
                raise ValueError("Invalid agent_str format")
        return values
