from pydantic import BaseModel

from lyfe_python_env.datatype.unity_vector3 import UnityVector3


class UnityTransform(BaseModel):
    position: UnityVector3
    rotation: UnityVector3

