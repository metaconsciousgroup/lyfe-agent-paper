from typing import Optional
from pydantic import BaseModel


class UnityUser(BaseModel):
    id: str
    username: str
    nameFirst: Optional[str] = None
    nameLast: Optional[str] = None
