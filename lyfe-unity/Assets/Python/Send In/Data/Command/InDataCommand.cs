using JsonSubTypes;
using Newtonsoft.Json;

[JsonConverter(typeof(JsonSubtypes), "cmdType")]
[JsonSubtypes.KnownSubType(typeof(InDataCommandSceneLoad), PythonCommandType.SCENE_LOAD)]
[JsonSubtypes.KnownSubType(typeof(InDataCommandSummonAgent), PythonCommandType.SUMMON_AGENT)]
[JsonSubtypes.KnownSubType(typeof(InDataCommandSummonItem), PythonCommandType.SUMMON_ITEM)]
[JsonSubtypes.KnownSubType(typeof(InDataCommandCharacterLookAt), PythonCommandType.CHARACTER_LOOK_AT)]
[JsonSubtypes.KnownSubType(typeof(InDataCommandCharacterLookAtClear), PythonCommandType.CHARACTER_LOOK_AT_CLEAR)]
[JsonSubtypes.KnownSubType(typeof(InDataCommandCharacterEmote), PythonCommandType.CHARACTER_EMOTE)]
[JsonSubtypes.KnownSubType(typeof(InDataCommandAgentMoveDestinationLocation), PythonCommandType.AGENT_MOVE_DESTINATION_LOCATION)]
[JsonSubtypes.KnownSubType(typeof(InDataCommandAgentMoveDestinationCharacter), PythonCommandType.AGENT_MOVE_DESTINATION_CHARACTER)]
[JsonSubtypes.KnownSubType(typeof(InDataCommandAgentMoveStop), PythonCommandType.AGENT_MOVE_STOP)]
[System.Serializable]
public class InDataCommand
{
    /// <summary>
    /// Command type, this is used to understand what kind of task implementation this is.
    /// All types are defined in class PythonCommandType.cs
    /// </summary>
    public string cmdType;
}