

[System.Serializable]
public class PythonSendOutPlayerRemoved : PythonSendOutPlayer
{

    public PythonSendOutPlayerRemoved() { }

    public PythonSendOutPlayerRemoved(string playerId) : base(PythonSendOutMessageType.PLAYER_REMOVED, playerId, /* locaions= */ new string[] { }) { }

    public static PythonSendOutPlayerRemoved From(CharacterEntity character) => new PythonSendOutPlayerRemoved(character.GetUser().Id.GetValue());
}
