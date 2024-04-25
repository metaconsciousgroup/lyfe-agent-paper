using System.Linq;

[System.Serializable]
public class PythonSendOutPlayerAdded : PythonSendOutPlayer
{
    public string username;
    public string characterModelPath;
    public TransformData transform;


    public PythonSendOutPlayerAdded() { }

    public PythonSendOutPlayerAdded(string playerId, string username, string characterModelPath, TransformData transform, string[] locations) :
        base(PythonSendOutMessageType.PLAYER_ADDED, playerId, locations)
    {
        this.username = username;
        this.characterModelPath = characterModelPath;
        this.transform = transform;
    }


    public static PythonSendOutPlayerAdded From(CharacterEntity character)
    {
        UserEntity user = character.GetUser();

        return new PythonSendOutPlayerAdded(
            user.Id.GetValue(),
            user.Username.GetValue(),
            character.GetReadyPlayerMeAvatarRenderer().GetUrl(),
            TransformData.From(character.transform),
            character.GetNearByAreas().GetAll().Select(i => i.GetKey()).ToArray()
        );
    }
}