
[System.Serializable]
public abstract class PythonSendOutTask : PythonSendOut
{
    public string taskId;
    
    public PythonSendOutTask(){}

    public PythonSendOutTask(string messageType, string taskId): base(messageType)
    {
        this.taskId = taskId;
    }
}
