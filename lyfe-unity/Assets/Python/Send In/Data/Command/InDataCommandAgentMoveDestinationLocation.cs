
[System.Serializable]
public class InDataCommandAgentMoveDestinationLocation : InDataCommandAgent
{
    public string targetLocation;

    public static InDataCommandAgentMoveDestinationLocation From(string agentId, string targetLocation)
    {
        return new()
        {
            cmdType = PythonCommandType.AGENT_MOVE_DESTINATION_LOCATION,
            agentId = agentId,
            targetLocation = targetLocation
        };
    }
}