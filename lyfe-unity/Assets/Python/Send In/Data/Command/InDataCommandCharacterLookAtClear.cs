
[System.Serializable]
public class InDataCommandCharacterLookAtClear : InDataCommand
{
    public string userId;

    public static InDataCommandCharacterLookAtClear From(string userId)
    {
        return new InDataCommandCharacterLookAtClear()
        {
            cmdType = PythonCommandType.CHARACTER_LOOK_AT_CLEAR,
            userId = userId
        };
    }
}
