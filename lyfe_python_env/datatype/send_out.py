from enum import IntEnum
from pydantic import BaseModel, Field, SerializeAsAny
from typing import List, Optional

from lyfe_python_env.datatype.unity_agent import UnityAgent
from lyfe_python_env.datatype.unity_character import UnityCharacter
from lyfe_python_env.datatype.unity_lobby import UnityLobby
from lyfe_python_env.datatype.unity_transform import UnityTransform
from lyfe_python_env.datatype.unity_user import UnityUser

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


class OutDataAgent(BaseModel):
    user: UnityUser
    character: Optional[UnityCharacter] = None
    transform: Optional[UnityTransform] = None


class OutDataScene(BaseModel):
    """This class contains information needed to load a scene directly from the Build or from an AssetBundle."""

    name: str  # This is currently used by the Unity server to load the scene from the Build
    title: Optional[str] = None  # TODO use this field for rendering in the UI
    # TODO use this field to locate an AssetBundle, if this is empty, the scene is loaded from the Build through `name`
    assetBundleUrl: Optional[str] = None
    # TODO use this field to load the scene from the AssetBundle
    assetBundleName: Optional[str] = None
    # TODO Remove this once we rely on Unity to send us the location list.
    agents: List[OutDataAgent]


class SendOutUnityCommandBase(BaseModel):
    """This class contains commands to be sent to Unity where an acknowledgement can be expected."""

    waitForAck: Optional[bool] = None
    waitForAckTimeout: Optional[float] = None
    commandId: str  # A unique identifier for this command, used to match the acknowledgement from Unity


class OutDataAgentLocation(SendOutUnityCommandBase):
    """This class contains information about an agent's location in a scene."""

    messageType: str = Field(default=SEND_OUT_AGENTS_SPAWN_LOCATION_MESSAGE)
    agents: List[OutDataAgent]


class OutDataGame(SendOutUnityCommandBase):
    messageType: str = Field(default=SEND_OUT_GAME_DATA)
    clientAuth: Optional[bool] = None
    lobby: Optional[UnityLobby] = None
    scene: OutDataScene


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


def out_agent_from_unity_agent(unity_agent: UnityAgent) -> OutDataAgent:
    return OutDataAgent(
        user=unity_agent.user,
        character=unity_agent.character,
        transform=unity_agent.transform,
    )
