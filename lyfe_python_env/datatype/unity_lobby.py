from typing import List
from pydantic import BaseModel


from lyfe_python_env.datatype.unity_character import UnityCharacter


class UnityLobby(BaseModel):
    characters: List[UnityCharacter]
