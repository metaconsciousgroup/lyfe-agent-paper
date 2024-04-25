
[System.Serializable]
public abstract class PythonSendOut
{
    public string messageType;
    
    public PythonSendOut(){}

    public PythonSendOut(string messageType)
    {
        this.messageType = messageType;
    }
}
