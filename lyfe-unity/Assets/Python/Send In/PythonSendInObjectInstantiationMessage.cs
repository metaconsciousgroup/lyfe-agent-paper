
[System.Serializable]
public class PythonSendInObjectInstantiationMessage : PythonSendInAgent
{
    // TODO: This should be an enum rather than a string
    public string objectType;
    public TransformData transform;
}
