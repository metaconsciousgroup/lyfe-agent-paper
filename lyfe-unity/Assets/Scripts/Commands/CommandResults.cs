
/// <summary>
/// 
/// </summary>
public class CommandResults
{
    public int count;
    public int countSuccess;
    public int countFailed;
    public bool skipped;
    public bool success => countFailed <= 0;
    public readonly CommandResult[] array;

    public CommandResults(int count)
    {
        this.count = count;
        array = new CommandResult[count];
    }
}
