
[System.Serializable]
public abstract class PythonSendOutPlayer : PythonSendOut
{
    public string playerId;
    public string[] locations;

    public PythonSendOutPlayer(){}

    public PythonSendOutPlayer(string messageType, string playerId, string[] locations): base(messageType)
    {
        this.playerId = playerId;
        this.locations = locations;
    }
}
