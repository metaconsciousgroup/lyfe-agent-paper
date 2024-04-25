
[System.Serializable]
public class PythonSendOutServerState : PythonSendOut
{
    public ServerState state;

    public PythonSendOutServerState(){}

    public PythonSendOutServerState(ServerState state): base(PythonSendOutMessageType.SERVER_STATE)
    {
        this.state = state;
    }

    public enum ServerState
    {
        STOPPED,
        STARTING,
        STARTED,
        STOPPING
    }
}
