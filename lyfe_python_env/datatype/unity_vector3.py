from pydantic import BaseModel

class UnityVector3(BaseModel):
    x: float
    y: float
    z: float
    
    @classmethod
    def zero(cls):
        return cls(x=0, y=0, z=0)
