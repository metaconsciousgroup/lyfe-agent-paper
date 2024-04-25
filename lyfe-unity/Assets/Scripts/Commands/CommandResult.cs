
public class CommandResult
{
    public InDataCommand command;
    public readonly bool success;
    public readonly bool skipped;
    public readonly ErrorData errorData;
    
    /// <summary>
    /// Constructor.
    /// </summary>
    /// <param name="command"></param>
    /// <param name="success"></param>
    /// <param name="errorData"></param>
    private CommandResult(InDataCommand command, bool success, bool skipped, ErrorData errorData)
    {
        this.command = command;
        this.success = success;
        this.skipped = skipped;
        this.errorData = errorData;
    }

    public static CommandResult Success(InDataCommand command) => new(command, true, false, null);
    
    public static CommandResult Failed(InDataCommand command, ErrorData errorData) => new(command, false, false, errorData);
    
    public static CommandResult Skipped(InDataCommand command) => new(command, false, true, null);
}
