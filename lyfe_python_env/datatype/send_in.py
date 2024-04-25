from pydantic import BaseModel
from typing import List, Optional, Union
from enum import Enum
from lyfe_python_env.datatype import UnityTransform


SEND_IN_AGENT_CHAT_MESSAGE = "AGENT_CHAT_MESSAGE"
SEND_IN_AGENT_DIRECT_MESSAGE = "AGENT_DIRECT_MESSAGE"
SEND_IN_AGENT_MOVE_ENDED = "AGENT_MOVE_ENDED"
SEND_IN_CHARACTER_PROXIMITY = "CHARACTER_PROXIMITY"
SEND_IN_PLAYER_ADDED = "PLAYER_ADDED"
SEND_IN_PLAYER_UPDATED = "PLAYER_UPDATED"
SEND_IN_PLAYER_REMOVED = "PLAYER_REMOVED"
SEND_IN_PLAYER_CHAT_MESSAGE = "PLAYER_CHAT_MESSAGE"
SEND_IN_PLAYER_DIRECT_MESSAGE = "PLAYER_DIRECT_MESSAGE"
SEND_IN_TASK_COMPLETED_MESSAGE = "TASK_COMPLETED_MESSAGE"
SEND_IN_TASK_STARTED_MESSAGE = "TASK_STARTED_MESSAGE"
SEND_IN_AGENT_FEEDBACK = "FEEDBACK"


class SendIn(BaseModel):  # Base class
    messageType: str


class SendInTaskBase(SendIn):
    commandId: Optional[
        str
    ] = None  # Unity will send back this command id in the acknowledgement message


class InCharacterProximityNearBy(BaseModel):
    players: Optional[List[str]] = []
    agents: Optional[List[str]] = []
    locations: Optional[List[str]] = []


class InCharacterProximityVisible(BaseModel):
    players: Optional[List[str]] = []
    agents: Optional[List[str]] = []


class InCharacterProximityPlayer(BaseModel):
    playerId: str
    transform: Optional[UnityTransform] = None
    nearBy: Optional[InCharacterProximityNearBy] = None
    messageType: str = SEND_IN_CHARACTER_PROXIMITY


class InCharacterProximityAgent(BaseModel):
    agentId: str
    transform: Optional[UnityTransform] = None
    nearBy: Optional[InCharacterProximityNearBy] = None
    visibility: Optional[InCharacterProximityVisible] = None
    messageType: str = SEND_IN_CHARACTER_PROXIMITY


class SendInAgent(SendIn):
    agentId: str
    locations: Optional[List[str]] = None


class SendInAgentChatMessage(SendInAgent):
    message: str
    receiverPlayerIds: Optional[List[str]] = []
    receiverAgentIds: Optional[List[str]] = []


class SendInAgentDirectMessage(SendInAgent):
    message: str
    receiverId: str


class SendInAgentMovementEnded(SendInAgent):
    arrivalDestination: str


class SendInAgentFeedback(SendInAgent):
    message: str


class SendInCharacterProximity(SendIn):
    players: Optional[List[InCharacterProximityPlayer]] = []
    agents: Optional[List[InCharacterProximityAgent]] = []


class SendInPlayer(SendIn):
    playerId: str
    locations: Optional[List[str]] = []


class SendInPlayerInfo(SendInPlayer):
    username: str
    nameFirst: Optional[str] = None
    nameLast: Optional[str] = None
    characterModelPath: Optional[str] = None
    transform: Optional[UnityTransform] = None


class SendInPlayerAdded(SendInPlayerInfo):
    pass


class SendInPlayerUpdated(SendInPlayerInfo):
    pass


class SendInPlayerRemoved(SendInPlayer):
    pass


class SendInPlayerChatMessage(SendInPlayer):
    message: str
    receiverPlayerIds: Optional[List[str]] = []
    receiverAgentIds: Optional[List[str]] = []


class SendInPlayerDirectMessage(SendInPlayer):
    message: str
    receiverId: str


class InLocationShapeCircle(BaseModel):
    kind: str
    radius: float


class InLocationShapeCircleOutline(BaseModel):
    kind: str
    radius: float


class InLocationShapeRect(BaseModel):
    kind: str
    x: float
    z: float


class InLocationShapeRectOutline(BaseModel):
    kind: str
    x: float
    z: float


class InLocationShapePoint(BaseModel):
    kind: str


InLocationShape = Union[
    InLocationShapeCircle,
    InLocationShapeCircleOutline,
    InLocationShapeRect,
    InLocationShapeRectOutline,
    InLocationShapePoint,
]


class InSpawnLocation(BaseModel):
    """This class contains information about a spawn location in a scene."""

    transform: UnityTransform
    shape: InLocationShape


class InNamedLocation(BaseModel):
    """This class contains information about a named location in a scene.

    Note: This may not be a spawn location.
    """

    name: str
    transform: UnityTransform
    shape: InLocationShape


class InSceneInformation(BaseModel):
    """This class contains information retrieved from the Unity server about the current scene."""

    name: str  # This should map to the same name as in a `UnitySceneIdentifier`
    locations: List[InNamedLocation]
    spawns: List[InSpawnLocation]


class InAgentsInformation(BaseModel):
    """This class contains information retrieved from the Unity server about the current scene."""

    pass


CompletedMessageMetadata = Union[InSceneInformation, InAgentsInformation]


class UnityCommandType(Enum):
    LOAD_SCENE = "load_scene"
    SPAWN_AGENTS = "spawn_agents"


class SendInTaskCompletedMessage(SendInTaskBase):
    """This message is used for telling Python that a task is completed.

    A task could be a scene is loaded, or agents are spawned.
    """

    cmd_type: UnityCommandType
    metadata: CompletedMessageMetadata


class SendInTaskStartedMessage(SendInTaskBase):
    """This message is used for telling Python that a task is started.

    A task could be loading a scene, or spawning agents.
    """

    cmd_type: UnityCommandType
