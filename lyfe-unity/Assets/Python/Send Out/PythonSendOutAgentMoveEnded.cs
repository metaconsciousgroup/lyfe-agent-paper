
[System.Serializable]
public class PythonSendOutAgentMoveEnded : PythonSendOutAgent
{
    public string arrivalDestination;

    public PythonSendOutAgentMoveEnded() { }

    public PythonSendOutAgentMoveEnded(string agentId, string arrivalDestination) : base(PythonSendOutMessageType.AGENT_MOVE_ENDED, agentId, new string[] { arrivalDestination })
    {
        this.arrivalDestination = arrivalDestination;
    }
}
