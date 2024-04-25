
[System.Serializable]
public class InDataCommandSummonAgent : InDataCommand
{
    public InDataAgent agent;

    public static InDataCommandSummonAgent From(InDataAgent agent)
    {
        return new()
        {
            cmdType = PythonCommandType.SUMMON_AGENT,
            agent = agent
        };
    }
}
