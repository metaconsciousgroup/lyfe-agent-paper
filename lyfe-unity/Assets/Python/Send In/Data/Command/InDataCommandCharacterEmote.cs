
/// <summary>
/// Handles command - character emote.
/// </summary>
[System.Serializable]
public class InDataCommandCharacterEmote : InDataCommand
{
    /// <summary>
    /// Id of the user which should be used.
    /// </summary>
    public string userId;
    /// <summary>
    /// Should emote be set active or inactive (play or stop).
    /// Note that setting emote inactive takes into account emoteId also.
    /// </summary>
    public bool emoteActive;
    /// <summary>
    /// Unique id of the emote, each emote is defined in SOEmote.cs with unique EmoteKind.cs id.
    /// </summary>
    public int emoteId;
    /// <summary>
    /// Emote play time in seconds, if -1 or less than zero, time player will be ignored.
    /// </summary>
    public float emotePlayTime;



    public static InDataCommandCharacterEmote From(string userId, bool emoteActive, int emoteId) => From(userId, emoteActive, emoteId, -1f);
    
    public static InDataCommandCharacterEmote From(string userId, bool emoteActive, int emoteId, float emotePlayTime)
    {
        return new InDataCommandCharacterEmote()
        {
            cmdType = PythonCommandType.CHARACTER_EMOTE,
            userId = userId,
            emoteActive = emoteActive,
            emoteId = emoteId,
            emotePlayTime = emotePlayTime
        };
    }
}