from collections import defaultdict
import logging
from typing import Any, List

from lyfe_python_env.datatype import UnityUser, UnityCharacter, UnityAgent
from lyfe_python_env.datatype.send_in import (
    SEND_IN_AGENT_FEEDBACK,
    SEND_IN_AGENT_MOVE_ENDED,
    SEND_IN_AGENT_CHAT_MESSAGE,
    SEND_IN_CHARACTER_PROXIMITY,
    SEND_IN_AGENT_DIRECT_MESSAGE,
    SEND_IN_PLAYER_ADDED,
    SEND_IN_PLAYER_UPDATED,
    SEND_IN_PLAYER_REMOVED,
    SEND_IN_PLAYER_CHAT_MESSAGE,
    SEND_IN_PLAYER_DIRECT_MESSAGE,
    SEND_IN_TASK_STARTED_MESSAGE,
    SEND_IN_TASK_COMPLETED_MESSAGE,
    SendInAgentFeedback,
    SendInAgentMovementEnded,
    SendInAgentChatMessage,
    SendInAgentDirectMessage,
    SendInPlayerAdded,
    SendInPlayerUpdated,
    SendInPlayerRemoved,
    SendInPlayerChatMessage,
    SendInPlayerDirectMessage,
    SendInCharacterProximity,
    SendInTaskStartedMessage,
    SendInTaskCompletedMessage,
)
from lyfe_python_env.datatype.unity_player import UnityPlayer
from lyfe_python_env.unity_resources import UnityResources

logger = logging.getLogger(__name__)


def log_event(
    event_type: str,
    user_type: str,
    user_id: str,
    username: str,
    observation_type: str,
    extra_info: dict = None,
):
    info = {
        "event_type": event_type,
        "user_type": user_type,
        "user_id": user_id,
        "username": username,
        "observation_type": observation_type,
    }
    if extra_info is not None:
        info.update(extra_info)

    msgs = [f"\n\t{key}: {value}" for key, value in info.items()]
    logger.debug(f"{' '.join(msgs)}")


def process_incoming(
    msg_dict: dict,
    unity_resources: UnityResources,
    agent_messages: defaultdict[str, List[Any]],
) -> None:
    """Process incoming messages from Unity in TextSideChannel."""
    if msg_dict is None:
        return

    message_type = msg_dict.get("messageType", None)

    if message_type == SEND_IN_CHARACTER_PROXIMITY:
        __process_incoming_handler_character_proximity(
            SendInCharacterProximity(**msg_dict),
            unity_resources=unity_resources,
        )
        data: SendInCharacterProximity = SendInCharacterProximity(**msg_dict)
        for agent in data.agents:
            agent_messages[agent.agentId].append(agent)

    elif message_type == SEND_IN_AGENT_CHAT_MESSAGE:
        data: SendInAgentChatMessage = SendInAgentChatMessage(**msg_dict)
        for receiverId in data.receiverAgentIds:
            agent_messages[receiverId].append(data)

    elif message_type == SEND_IN_AGENT_DIRECT_MESSAGE:
        data: SendInAgentDirectMessage = SendInAgentDirectMessage(**msg_dict)
        agent_messages[data.receiverId].append(data)

    elif message_type == SEND_IN_AGENT_MOVE_ENDED:
        data: SendInAgentMovementEnded = SendInAgentMovementEnded(**msg_dict)
        agent_messages[data.agentId].append(data)

    elif message_type == SEND_IN_PLAYER_CHAT_MESSAGE:
        data: SendInPlayerChatMessage = SendInPlayerChatMessage(**msg_dict)
        for receiverId in data.receiverAgentIds:
            agent_messages[receiverId].append(data)

    elif message_type == SEND_IN_PLAYER_DIRECT_MESSAGE:
        data: SendInPlayerDirectMessage = SendInPlayerDirectMessage(**msg_dict)
        agent_messages[data.receiverId].append(data)

    elif message_type == SEND_IN_PLAYER_ADDED:
        data: SendInPlayerAdded = SendInPlayerAdded(**msg_dict)
        __process_incoming_handler_player_added(data, unity_resources=unity_resources)
        for q in agent_messages.values():
            q.append(data)
    elif message_type == SEND_IN_PLAYER_UPDATED:
        data: SendInPlayerUpdated = SendInPlayerUpdated(**msg_dict)
        __process_incoming_handler_player_updated(data, unity_resources=unity_resources)
    elif message_type == SEND_IN_PLAYER_REMOVED:
        data: SendInPlayerRemoved = SendInPlayerRemoved(**msg_dict)
        __process_incoming_handler_player_removed(data, unity_resources=unity_resources)
        for q in agent_messages.values():
            q.append(data)
    elif message_type == SEND_IN_TASK_COMPLETED_MESSAGE:
        data: SendInTaskCompletedMessage = SendInTaskCompletedMessage(**msg_dict)
        __process_task_completed_message(data)

    elif message_type == SEND_IN_TASK_STARTED_MESSAGE:
        data: SendInTaskStartedMessage = SendInTaskStartedMessage(**msg_dict)
        __process_task_started_message(data)

    elif message_type == SEND_IN_AGENT_FEEDBACK:
        data: SendInAgentFeedback = SendInAgentFeedback(**msg_dict)
        agent_messages[data.agentId].append(data)

    else:
        logger.warning(
            f"Unrecognized messageType: {message_type} [{msg_dict}] Skipping"
        )


def __process_incoming_handler_player_added(
    data: SendInPlayerAdded, unity_resources: UnityResources
):
    logger.info("Player joined: {0}".format(data))

    # construct new player
    unity_user: UnityUser = UnityUser(
        id=data.playerId,
        username=data.username,
        nameFirst=data.nameFirst,
        nameLast=data.nameLast,
    )
    character: UnityCharacter = None
    if data.characterModelPath is not None:
        character = UnityCharacter(modelPath=data.characterModelPath)
    player: UnityPlayer = UnityPlayer(
        user=unity_user, character=character, transform=data.transform
    )

    if unity_resources.add_player(player):
        log_event(
            SEND_IN_PLAYER_ADDED, "PLAYER", unity_user.id, unity_user.username, "N/A"
        )
    else:
        logger.warning("Fail to join new player with id '{0}'".format(unity_user.id))


def __process_incoming_handler_player_updated(
    data: SendInPlayerUpdated, unity_resources: UnityResources
):
    logger.debug("Player updated: {0}".format(data))

    # construct updated player
    unity_user: UnityUser = UnityUser(
        id=data.playerId,
        username=data.username,
        nameFirst=data.nameFirst,
        nameLast=data.nameLast,
    )
    character: UnityCharacter = UnityCharacter(modelPath=data.characterModelPath)
    player: UnityPlayer = UnityPlayer(
        user=unity_user, character=character, transform=data.transform
    )

    if unity_resources.update_player(player):
        log_event(
            SEND_IN_PLAYER_UPDATED, "PLAYER", unity_user.id, unity_user.username, "N/A"
        )
    else:
        logger.warning("Fail to update player with id '{0}'".format(unity_user.id))


def __process_incoming_handler_player_removed(
    data: SendInPlayerRemoved, unity_resources: UnityResources
):
    logger.debug("Player removed: {0}".format(data))

    if unity_resources.remove_player(data.playerId):
        log_event(SEND_IN_PLAYER_REMOVED, "PLAYER", data.playerId, "", "N/A")
    else:
        logger.warning("Fail to remove player id '{0}'".format(data.playerId))


def __process_incoming_handler_character_proximity(
    data: SendInCharacterProximity, unity_resources: UnityResources
):
    # update players
    for player in data.players:
        unity_player: UnityPlayer = unity_resources.get_player(player.playerId)
        if unity_player:
            unity_player.transform = player.transform
            unity_player.near_by.players = [
                p.user for p in unity_resources.get_players(player.nearBy.players)
            ]
            unity_player.near_by.agents = [
                a.user for a in unity_resources.get_agents(player.nearBy.agents)
            ]
            unity_player.near_by.locations = player.nearBy.locations

    # update agents
    for agent in data.agents:
        unity_agent: UnityAgent = unity_resources.get_agent(agent.agentId)
        if unity_agent:
            unity_agent.transform = agent.transform
            unity_agent.near_by.players = [
                p.user for p in unity_resources.get_players(agent.nearBy.players)
            ]
            unity_agent.near_by.agents = [
                a.user for a in unity_resources.get_agents(agent.nearBy.agents)
            ]
            unity_agent.near_by.locations = agent.nearBy.locations
            if agent.visibility is None:
                continue
            unity_agent.visibility.players = [
                p.user for p in unity_resources.get_players(agent.visibility.players)
            ]
            unity_agent.visibility.agents = [
                a.user for a in unity_resources.get_agents(agent.visibility.agents)
            ]


def __process_task_completed_message(data: SendInTaskCompletedMessage):
    logger.debug(SEND_IN_TASK_COMPLETED_MESSAGE + str(data))


def __process_task_started_message(data: SendInTaskStartedMessage):
    logger.debug(SEND_IN_TASK_STARTED_MESSAGE + str(data))
