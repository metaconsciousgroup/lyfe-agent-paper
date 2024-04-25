[System.Serializable]
public class PythonSendOutAgentDirectMessage : PythonSendOutAgent
{
    public string message;
    public string receiverId;

    public PythonSendOutAgentDirectMessage() { }

    public PythonSendOutAgentDirectMessage(string agentId, string receiverId, string message, string[] locations)
        : base(PythonSendOutMessageType.AGENT_DIRECT_MESSAGE, agentId, locations)
    {
        this.message = message;
        this.receiverId = receiverId;
    }
}
