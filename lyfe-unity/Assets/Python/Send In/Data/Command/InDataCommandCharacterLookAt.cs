
[System.Serializable]
public class InDataCommandCharacterLookAt : InDataCommand
{
    public string userId;
    public string targetEntityId;

    public static InDataCommandCharacterLookAt From(string userId, string targetEntityId)
    {
        return new InDataCommandCharacterLookAt()
        {
            cmdType = PythonCommandType.CHARACTER_LOOK_AT,
            userId = userId,
            targetEntityId = targetEntityId
        };
    }
}
