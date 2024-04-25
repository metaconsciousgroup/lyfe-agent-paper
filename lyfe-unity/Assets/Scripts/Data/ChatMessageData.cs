
using System.Collections.Generic;

public class ChatMessageData
{
    public CharacterEntity author;
    public string message;
    public string channelId;
    public HashSet<CharacterEntity> receiverPlayers;
    public HashSet<CharacterEntity> receiverAgents;
    
    public UserEntity user => author.GetUser();
    
    private ChatMessageData(CharacterEntity author, string message, string channelId):this(
        author,
        message,
        channelId,
        author.GetNearByCharacters().GetAllWithPermission(CharacterPermission.Player),
        author.GetNearByCharacters().GetAllWithPermission(CharacterPermission.Agent))
    { }
    
    private ChatMessageData(CharacterEntity author, string message, string channelId, HashSet<CharacterEntity> receiverPlayers, HashSet<CharacterEntity> receiverAgents)
    {
        this.author = author;
        this.message = message;
        this.channelId = channelId;
        this.receiverPlayers = receiverPlayers;
        this.receiverAgents = receiverAgents;
    }

    
    public static string GetDirectChannelId(AgentEntity agentEntity) => GetDirectChannelId(agentEntity.GetCharacter());
    public static string GetDirectChannelId(CharacterEntity characterEntity) => GetDirectChannelId(characterEntity.GetUser());
    public static string GetDirectChannelId(UserEntity userEntity) => userEntity.Id.GetValue();

    public static ChatMessageData From(CharacterEntity author, string message, string channelId) => new (
        author,
        message,
        channelId);
    
    public static ChatMessageData From(CharacterEntity author, string message, string channelId, HashSet<CharacterEntity> receiverPlayers, HashSet<CharacterEntity> receiverAgents) => new (
        author,
        message,
        channelId,
        receiverPlayers,
        receiverAgents);
}
