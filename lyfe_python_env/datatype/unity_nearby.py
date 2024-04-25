from typing import List
from pydantic import BaseModel, Field

from lyfe_python_env.datatype.unity_user import UnityUser


class UnityNearBy(BaseModel):
    players: List[UnityUser] = Field(default_factory=list)
    agents: List[UnityUser] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)

class UnityVisibility(BaseModel):
    players: List[UnityUser] = Field(default_factory=list)
    agents: List[UnityUser] = Field(default_factory=list)
