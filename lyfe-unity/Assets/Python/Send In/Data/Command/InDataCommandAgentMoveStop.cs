
[System.Serializable]
public class InDataCommandAgentMoveStop : InDataCommandAgent
{

    public static InDataCommandAgentMoveStop From(string agentId)
    {
        return new InDataCommandAgentMoveStop()
        {
            cmdType = PythonCommandType.AGENT_MOVE_STOP,
            agentId = agentId
        };
    }
}
