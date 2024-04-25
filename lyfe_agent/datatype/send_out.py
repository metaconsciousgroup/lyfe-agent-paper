from enum import IntEnum
from pydantic import BaseModel, Field, SerializeAsAny
from typing import List, Optional

from lyfe_python_env.datatype.unity_transform import UnityTransform

SEND_OUT_GAME_DATA = "GAME_DATA"
SEND_OUT_AGENT_CHAT_MESSAGE = "AGENT_CHAT_MESSAGE"
SEND_OUT_AGENT_CODE_MESSAGE = "AGENT_CODE_MESSAGE"
SEND_OUT_AGENT_DIRECT_MESSAGE = "AGENT_DIRECT_MESSAGE"
SEND_OUT_AGENT_MOVE_DESTINATION_LOCATION = "AGENT_MOVE_DESTINATION_LOCATION"
SEND_OUT_OBJECT_INSTANTICATION = "OBJECT_INSTANTIATION_MESSAGE"
SEND_OUT_AGENTS_SPAWN_LOCATION_MESSAGE = "AGENTS_SPAWN_LOCATION_MESSAGE"

SEND_OUT_TASK = "TASK"
SEND_OUT_CHARACTER_EMOTE_TASK = "CHARACTER_EMOTE"
SEND_OUT_CHARACTER_LOOK_AT_TASK = "CHARACTER_LOOK_AT"
SEND_OUT_AGENT_MOVE_STOP_TASK = "AGENT_MOVE_STOP"

class SendOutAgent(BaseModel):
    agentId: str
    messageType: str


class SendOutAgentChatMessage(SendOutAgent):
    message: str
    messageType: str = Field(default=SEND_OUT_AGENT_CHAT_MESSAGE)


class SendOutAgentCodeMessage(SendOutAgent):
    message: str
    messageType: str = Field(default=SEND_OUT_AGENT_CODE_MESSAGE)


class SendOutAgentDirectMessage(SendOutAgent):
    message: str
    receiverId: str
    messageType: str = Field(default=SEND_OUT_AGENT_DIRECT_MESSAGE)


class SendOutAgentMoveLocation(SendOutAgent):
    location: str
    messageType: str = Field(default=SEND_OUT_AGENT_MOVE_DESTINATION_LOCATION)


class SendOutObjectInstantiation(SendOutAgent):
    messageType: str = Field(default=SEND_OUT_OBJECT_INSTANTICATION)
    objectType: str  # TODO: This should be an enum of possible instantiable objects
    transform: UnityTransform


class SendOutDataCommand(BaseModel):
    cmdType: str

class SendOutTask(BaseModel):
    messageType: str = Field(default=SEND_OUT_TASK)
    taskId: str
    waitForResponse: bool
    commands: List[SerializeAsAny[SendOutDataCommand]]

class EmoteKind(IntEnum):
    Wave = 1
    Point = 2
    Guitar = 3
    Laugh = 4
    PhoneCall = 5
    Talking = 100

class SendOutCharacterEmote(SendOutDataCommand):
    cmdType: str = Field(default=SEND_OUT_CHARACTER_EMOTE_TASK)
    userId: str
    emoteId: EmoteKind
    emoteActive: bool
    emotePlayTime: Optional[float] = -1

class SendOutCharacterLookAt(SendOutDataCommand):
    cmdType: str = Field(default=SEND_OUT_CHARACTER_LOOK_AT_TASK)
    userId: str
    targetEntityId: str

class SendOutAgentMoveStop(SendOutDataCommand):
    cmdType: str = Field(default=SEND_OUT_AGENT_MOVE_STOP_TASK)
    agentId: str
