
using System.Collections.Generic;
using System.Linq;

[System.Serializable]
public class PythonSendOutPlayerChatMessage : PythonSendOutPlayer
{
    public string message;
    public string[] receiverPlayerIds;
    public string[] receiverAgentIds;

    public PythonSendOutPlayerChatMessage() { }

    public PythonSendOutPlayerChatMessage(
        string playerId,
        string[] receiverPlayerIds,
        string[] receiverAgentIds,
        string[] locations,
        string message) : base(PythonSendOutMessageType.PLAYER_CHAT_MESSAGE, playerId, locations)
    {
        this.receiverPlayerIds = receiverPlayerIds;
        this.receiverAgentIds = receiverAgentIds;
        this.message = message;
    }

    public static PythonSendOutPlayerChatMessage From(CharacterEntity characterEntity, string message)
    {
        NearByCharacters nearBy = characterEntity.GetNearByCharacters();
        HashSet<CharacterEntity> nearByPlayers = nearBy.GetAllWithPermission(CharacterPermission.Player);
        HashSet<CharacterEntity> nearByAgents = nearBy.GetAllWithPermission(CharacterPermission.Agent);

        string playerId = characterEntity.GetUser().Id.GetValue();

        return new PythonSendOutPlayerChatMessage(
            playerId,    // Sender
            nearByPlayers.Select(i => i.GetUser().Id.GetValue()).ToArray(),
            nearByAgents.Select(i => i.GetUser().Id.GetValue()).ToArray(),
            characterEntity.GetNearByAreas().GetAll().Select(i => i.GetKey()).ToArray(),
            message);
    }
}
