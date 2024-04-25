from typing import Optional
from pydantic import BaseModel, Field

from lyfe_python_env.datatype.unity_character import UnityCharacter
from lyfe_python_env.datatype.unity_nearby import UnityNearBy, UnityVisibility
from lyfe_python_env.datatype.unity_transform import UnityTransform
from lyfe_python_env.datatype.unity_user import UnityUser


class UnityAgent(BaseModel):
    user: UnityUser
    character: Optional[UnityCharacter] = None
    transform: Optional[UnityTransform] = None
    near_by: UnityNearBy = Field(default_factory=UnityNearBy)
    visibility: UnityVisibility = Field(default_factory=UnityVisibility)
