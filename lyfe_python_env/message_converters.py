import logging
import time
from lyfe_python_env.datatype.send_out import (
    EmoteKind,
    SendOutAgentChatMessage,
    SendOutAgentCodeMessage,
    SendOutAgentDirectMessage,
    SendOutAgentMoveLocation,
    SendOutAgentMoveStop,
    SendOutCharacterEmote,
    SendOutCharacterLookAt,
    SendOutObjectInstantiation,
    SendOutTask,
)

logger = logging.getLogger(__name__)


def convert_to_actions(action, agent_id) -> list:
    """Converts the action from the Python agent to the Unity agent.

    AI (Python)->Environment (Unity)
    """
    data = []

    # This is the latest way to send unity commands.
    task_commands = []
    action_chat_message: str = action.get("talk", None)
    if action_chat_message is not None:
        data.append(
            SendOutAgentChatMessage(agentId=agent_id, message=action_chat_message)
        )

    action_code_message: str = action.get("code", None)
    if action_code_message is not None:
        data.append(
            SendOutAgentCodeMessage(agentId=agent_id, message=action_code_message)
        )

    action_animation: str = action.get("anim", None)
    if action_animation == "Talking":
        task_commands.append(
            SendOutCharacterEmote(
                userId=agent_id,
                emoteId=EmoteKind.Talking,
                emoteActive=True,
                emotePlayTime=1.0 if action_chat_message is None else len(action_chat_message) / 10.0,
            )
        )
        task_commands.append(
            SendOutAgentMoveStop(
                agentId=agent_id,
            )
        )

    action_look_at: str = action.get("look_at", None)
    if action_look_at is not None:
        task_commands.append(
            SendOutCharacterLookAt(
                userId=agent_id,
                targetEntityId=action_look_at,
            )
        )

    action_dm = action.get("message", None)
    if action_dm is not None:
        action_dm_message, receiverId = action_dm
        if receiverId is not None:
            data.append(
                SendOutAgentDirectMessage(
                    agentId=agent_id,
                    message=action_dm_message,
                    receiverId=receiverId,
                )
            )
            task_commands.append(
                SendOutCharacterEmote(
                    userId=agent_id,
                    emoteId=EmoteKind.PhoneCall,
                    emoteActive=True,
                )
            )

    action_move_location: str = action.get("choose_destination", None)
    if action_move_location is not None:
        data.append(
            SendOutAgentMoveLocation(agentId=agent_id, location=action_move_location)
        )

    action_instantiate_object = action.get("instantiate_object", None)
    if action_instantiate_object is not None:
        data.append(
            SendOutObjectInstantiation(
                agentId=agent_id,
                objectType=action_instantiate_object.get("objectType", None),
                transform=action_instantiate_object.get("transform", None),
            )
        )

    if len(task_commands) > 0:
        task_id = "task_{0}_{1}".format(agent_id, time.time())
        data.append(
            SendOutTask(
                taskId=task_id,
                waitForResponse=False,
                commands=task_commands,
            )
        )
    return data
