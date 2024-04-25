using System.Collections.Generic;
using System.Linq;
using UnityEngine.Serialization;
using UnityEngine.UIElements;

[System.Serializable]
public class PythonSendOutCharacterProximity : PythonSendOut
{
    public DataPlayer[] players;
    public DataAgent[] agents;

    public PythonSendOutCharacterProximity() { }

    public PythonSendOutCharacterProximity(DataPlayer[] players, DataAgent[] agents) : base(PythonSendOutMessageType.CHARACTER_PROXIMITY)
    {
        this.players = players;
        this.agents = agents;
    }


    [System.Serializable]
    public class DataPlayer
    {
        public string playerId;
        public TransformData transform;
        public NearBy nearBy;

        public DataPlayer() { }

        public DataPlayer(string playerId, TransformData transform, NearBy nearBy)
        {
            this.playerId = playerId;
            this.transform = transform;
            this.nearBy = nearBy;
        }

        public static DataPlayer From(CharacterEntity character)
        {
            return new DataPlayer(
                character.GetUser().Id.GetValue(),
                TransformData.From(character.transform),
                NearBy.From(character.GetNearByCharacters(), character.GetNearByAreas())
            );
        }

        public static DataPlayer[] From(List<CharacterEntity> value)
        {
            if (value == null) return new DataPlayer[] { };
            int length = value.Count;

            DataPlayer[] array = new DataPlayer[length];
            for (int i = 0; i < length; i++) array[i] = From(value[i]);
            return array;
        }
    }

    [System.Serializable]
    public class DataAgent
    {
        public string agentId;
        public TransformData transform;
        public NearBy nearBy;

        public VisibilityData visibility;

        public DataAgent() { }

        public DataAgent(string agentId, TransformData transform, NearBy nearBy, VisibilityData visibility)
        {
            this.agentId = agentId;
            this.transform = transform;
            this.nearBy = nearBy;
            this.visibility = visibility;
        }

        public static DataAgent From(AgentEntity value)
        {
            return new DataAgent(
                value.GetCharacter().GetUser().Id.GetValue(),
                TransformData.From(value.GetCharacter().transform),
                NearBy.From(value.GetCharacter().GetNearByCharacters(),
                value.GetCharacter().GetNearByAreas()),
                VisibilityData.From(value.GetCharacter().GetVisibleCharacters())
                );
        }

        public static DataAgent[] From(List<AgentEntity> value)
        {
            if (value == null) return new DataAgent[] { };
            int length = value.Count;

            DataAgent[] array = new DataAgent[length];
            for (int i = 0; i < length; i++) array[i] = From(value[i]);
            return array;
        }

    }

    [System.Serializable]
    public class NearBy
    {
        public string[] players;
        public string[] agents;

        public string[] locations;

        public NearBy() { }

        public NearBy(string[] players, string[] agents, string[] locations)
        {
            this.players = players;
            this.agents = agents;
            this.locations = locations;
        }

        public static NearBy From(NearByCharacters value, NearByAreas nearByAreas)
        {
            HashSet<CharacterEntity> playerCharacters = value.GetAllWithPermission(CharacterPermission.Player);
            HashSet<CharacterEntity> agentCharacters = value.GetAllWithPermission(CharacterPermission.Agent);
            HashSet<LyfeCreatorWorldArea> locations = nearByAreas.GetAll();

            return new NearBy(
                playerCharacters.Select(i => i.GetUser().Id.GetValue()).ToArray(),
                agentCharacters.Select(i => i.GetUser().Id.GetValue()).ToArray(),
                locations.Select(i => i.GetKey()).ToArray()
            );
        }
    }

    [System.Serializable]
    public class VisibilityData
    {
        public string[] players;
        public string[] agents;

        public VisibilityData() { }

        public VisibilityData(string[] players, string[] agents)
        {
            this.players = players;
            this.agents = agents;
        }

        public static VisibilityData From(VisibleCharacters visibleCharacters)
        {
            HashSet<CharacterEntity> playerCharacters = visibleCharacters.GetAllWithPermission(CharacterPermission.Player);
            HashSet<CharacterEntity> agentCharacters = visibleCharacters.GetAllWithPermission(CharacterPermission.Agent);

            return new VisibilityData(
                playerCharacters.Select(i => i.GetUser().Id.GetValue()).ToArray(),
                agentCharacters.Select(i => i.GetUser().Id.GetValue()).ToArray()
            );
        }
    }

    public static PythonSendOutCharacterProximity From(AppGame appGame)
    {
        return new PythonSendOutCharacterProximity(
            new DataPlayer[] { },
            DataAgent.From(appGame.GetAgents().GetAll())
        );
    }
}
