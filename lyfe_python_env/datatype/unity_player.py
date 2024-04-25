from typing import Optional
from pydantic import BaseModel, Field

from lyfe_python_env.datatype.unity_user import UnityUser
from lyfe_python_env.datatype.unity_character import UnityCharacter
from lyfe_python_env.datatype.unity_transform import UnityTransform
from lyfe_python_env.datatype.unity_nearby import UnityNearBy


class UnityPlayer(BaseModel):
    user: UnityUser
    character: Optional[UnityCharacter] = None
    transform: Optional[UnityTransform] = None
    near_by: UnityNearBy = Field(default_factory=UnityNearBy)
