
// This class would annouce to the players when an agent is about to move.
using System.Collections.Generic;

public class AgentMoveData
{
    public CharacterEntity agent;
    public string locationName;

    public HashSet<CharacterEntity> receiverPlayers;


    private AgentMoveData(CharacterEntity agent, string locationName)
    {
        this.agent = agent;
        this.locationName = locationName;
        this.receiverPlayers = agent.GetNearByCharacters().GetAllWithPermission(CharacterPermission.Player);
    }

    public static AgentMoveData From(CharacterEntity agent, string locationName) => new(agent, locationName);
}