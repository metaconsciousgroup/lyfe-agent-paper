
[System.Serializable]
public class InDataCommandSummonItem : InDataCommand
{
    public InDataItem item;

    public static InDataCommandSummonItem From(InDataItem item)
    {
        return new()
        {
            cmdType = PythonCommandType.SUMMON_ITEM,
            item = item
        };
    }
}
