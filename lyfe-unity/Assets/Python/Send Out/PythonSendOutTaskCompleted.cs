
[System.Serializable]
public class PythonSendOutTaskCompleted : PythonSendOutTask
{
    /// <summary>
    /// Determines if completed task was successful.
    /// </summary>
    public bool success;
    /// <summary>
    /// Command results will only be included if success is false.
    /// </summary>
    public PythonSendOutCommandResult[] commands;
    
    public PythonSendOutTaskCompleted(){}

    public PythonSendOutTaskCompleted(string taskId, CommandResults results): base(PythonSendOutMessageType.TASK_COMPLETED, taskId)
    {
        this.success = results.success;
        if (!this.success)
        {
            int length = results.count;
            this.commands = new PythonSendOutCommandResult[length];
            
            for (int i = 0; i < length; i++)
            {
                CommandResult res = results.array[i];
                this.commands[i] = new PythonSendOutCommandResult(res.command.cmdType, res.success, res.skipped, res.errorData?.message);
            }
        }
    }

    /// <summary>
    /// Holds response data for each command result.
    /// </summary>
    [System.Serializable]
    public class PythonSendOutCommandResult
    {
        public string cmdType;
        public bool success;
        public bool skipped;
        public string error;

        public PythonSendOutCommandResult() { }

        public PythonSendOutCommandResult(string cmdType, bool success, bool skipped, string error)
        {
            this.cmdType = cmdType;
            this.success = success;
            this.skipped = skipped;
            this.error = error;
        }
    }
}
