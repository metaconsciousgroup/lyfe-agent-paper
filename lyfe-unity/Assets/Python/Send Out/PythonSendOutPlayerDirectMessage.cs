using System.Diagnostics;
using UnityEngine.Assertions;

[System.Serializable]
public class PythonSendOutPlayerDirectMessage : PythonSendOutPlayer
{
    public string message;
    public string receiverId;

    public PythonSendOutPlayerDirectMessage() { }

    public PythonSendOutPlayerDirectMessage(string playerId, string receiverId, string message, string[] locations) 
        : base(PythonSendOutMessageType.PLAYER_DIRECT_MESSAGE, playerId, locations) 
    {
        this.message = message;
        this.receiverId = receiverId;
    }
    public static PythonSendOutPlayerDirectMessage From(ChatMessageData chatMessageData, string[] locations)
    {
        string playerId = chatMessageData.author.GetUser().Id.GetValue();
        return new PythonSendOutPlayerDirectMessage(playerId, chatMessageData.channelId, chatMessageData.message, locations);
    }
}
