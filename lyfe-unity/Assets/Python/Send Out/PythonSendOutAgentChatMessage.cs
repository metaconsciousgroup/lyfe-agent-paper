using System.Collections.Generic;
using System.Linq;

[System.Serializable]
public class PythonSendOutAgentChatMessage : PythonSendOutAgent
{
    public string message;
    public string[] receiverPlayerIds;
    public string[] receiverAgentIds;
    
    public PythonSendOutAgentChatMessage() { }

    public PythonSendOutAgentChatMessage(
        string agentId,
        string message,
        string[] receiverPlayerIds,
        string[] receiverAgentIds,
        string[] locations
        ) : base(PythonSendOutMessageType.AGENT_CHAT_MESSAGE, agentId, locations)
    {
        this.message = message;
        this.receiverPlayerIds = receiverPlayerIds;
        this.receiverAgentIds = receiverAgentIds;
    }

    public static PythonSendOutAgentChatMessage From(ChatMessageData chatMessageData, string[] locations)
    {
        return new PythonSendOutAgentChatMessage(
            chatMessageData.author.GetUser().Id.GetValue(),
            chatMessageData.message,
            chatMessageData.receiverPlayers.Select(i => i.GetUser().Id.GetValue()).ToArray(),
            chatMessageData.receiverAgents.Select(i => i.GetUser().Id.GetValue()).ToArray(),
            locations
            );
    }
}
