
[System.Serializable]
public abstract class PythonSendOutAgent: PythonSendOut
{
    public string agentId; // agent id from whom came the message
    public string[] locations;
    
    public PythonSendOutAgent(){}

    public PythonSendOutAgent(string messageType, string agentId, string[]locations): base(messageType)
    {
        this.agentId = agentId;
        this.locations = locations;
    }

}
