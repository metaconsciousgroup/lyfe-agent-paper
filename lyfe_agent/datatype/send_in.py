from pydantic import BaseModel
from typing import List, Optional
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
    players: List[str]
    agents: List[str]
    locations: Optional[List[str]] = None


class InCharacterProximityVisible(BaseModel):
    players: Optional[List[str]] = None
    agents: Optional[List[str]] = None

class InCharacterProximityPlayer(BaseModel):
    playerId: str
    transform: UnityTransform
    nearBy: InCharacterProximityNearBy
    messageType: str = SEND_IN_CHARACTER_PROXIMITY

class InCharacterProximityAgent(BaseModel):
    agentId: str
    transform: UnityTransform
    nearBy: InCharacterProximityNearBy
    visibility: Optional[InCharacterProximityVisible] = None
    messageType: str = SEND_IN_CHARACTER_PROXIMITY

class SendInAgent(SendIn):
    agentId: str
    locations: Optional[List[str]] = None


class SendInAgentChatMessage(SendInAgent):
    message: str
    receiverPlayerIds: List[str]
    receiverAgentIds: List[str]


class SendInAgentDirectMessage(SendInAgent):
    message: str
    receiverId: str


class SendInAgentMovementEnded(SendInAgent):
    arrivalDestination: str

class SendInAgentFeedback(SendInAgent):
    message: str


class SendInCharacterProximity(SendIn):
    players: List[InCharacterProximityPlayer]
    agents: List[InCharacterProximityAgent]


class SendInPlayer(SendIn):
    playerId: str
    locations: Optional[List[str]] = None


class SendInPlayerInfo(SendInPlayer):
    username: str
    nameFirst: Optional[str] = None
    nameLast: Optional[str] = None
    characterModelPath: str
    transform: UnityTransform


class SendInPlayerAdded(SendInPlayerInfo):
    pass


class SendInPlayerUpdated(SendInPlayerInfo):
    pass


class SendInPlayerRemoved(SendInPlayer):
    pass


class SendInPlayerChatMessage(SendInPlayer):
    message: str
    receiverPlayerIds: List[str]
    receiverAgentIds: List[str]


class SendInPlayerDirectMessage(SendInPlayer):
    message: str
    receiverId: str