using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;
using Sirenix.OdinInspector;
using UnityEngine;

public class PythonCommandSimulator : BaseMonoBehaviour
{
    [SerializeField] private UnityDataMinMaxFloat _summonAgentRange;
    private string[] _summonAgentNames = new[]
    {
        "John", "Mary", "Robert", "Jennifer", "William", "Emily", "James", "Jessica", "Michael", "Elizabeth",
        "David", "Emma", "Richard", "Amanda", "Joseph", "Sarah", "Charles", "Ashley", "Thomas", "Melissa",
        "Daniel", "Laura", "Matthew", "Nicole", "Christopher", "Kimberly", "Andrew", "Stephanie", "Joseph", "Angela",
        "Brian", "Amy", "Kevin", "Rebecca", "Steven", "Christine", "Mark", "Rachel", "Anthony", "Katherine",
        "Paul", "Michelle", "Donald", "Laura", "George", "Samantha", "Kenneth", "Susan", "Steven", "Patricia",
        "Jonathan", "Olivia", "Ryan", "Grace", "Nicholas", "Hannah", "Eric", "Natalie", "Brandon", "Sophia",
        "Samuel", "Megan", "Benjamin", "Lauren", "Peter", "Victoria", "Jeremy", "Alexis", "Dylan", "Alyssa",
        "Caleb", "Alexandra", "Jared", "Kayla", "Logan", "Madison", "Nathan", "Brianna", "Scott", "Allison",
        "Justin", "Julia", "Tyler", "Hailey", "Jordan", "Ella", "Kyle", "Savannah", "Aaron", "Taylor",
        "Cameron", "Emma", "Austin", "Sydney", "Cody", "Chloe", "Derek", "Zoe", "Ethan", "Lily",
        "Gabriel", "Isabella", "Mason", "Abigail", "Elijah", "Sophie", "Christian", "Ava", "Nicholas", "Haley",
        "Isaac", "Brooklyn", "Wyatt", "Avery", "Luke", "Amelia", "Jackson", "Mia", "Liam", "Evelyn",
        "Owen", "Aubrey", "Evan", "Addison", "Colton", "Scarlett", "Aiden", "Nevaeh", "Blake", "Leah",
        "Cole", "Zoey", "Carson", "Lillian", "Gavin", "Audrey", "Hudson", "Claire", "Cooper", "Ariana",
        "Xavier", "Peyton", "Max", "Anna", "Leo", "Kylie", "Miles", "Jasmine", "Bryce", "Gabriella",
        "Tristan", "Maya", "Dominic", "Nora", "Harrison", "Alice", "Victor", "Eva", "Spencer", "Isabelle"
    };
    [SerializeField] private AppPythonWebSocket _python;
    
#if UNITY_EDITOR
    protected override void Reset()
    {
        base.Reset();
        _summonAgentRange = new UnityDataMinMaxFloat(2f, 5f);
    }
#endif

    [Title("Character Emotes")]
    [Button]
    public void SimulateRandomCharacterEmote(bool toggle = true)
    {
        if (!Logged_AppIsPlaying()) return;
        if (!Logged_GetRandomEmote(out SOEmote emote)) return;

        SimulateRandomCharacterEmote(emote, toggle);
    }
    
    [Button]
    public void SimulateRandomCharacterEmote(SOEmote emote, bool toggle = true, float playTime = -1)
    {
        if (!Logged_AppIsPlaying()) return;
        if (!Logged_GetRandomUser(out UserEntity user)) return;
        
        SimulateCharacterEmote(emote, user, toggle, playTime);
    }
    
    [Button]
    public void SimulateCharacterEmote(SOEmote emote, UserEntity user, bool toggle = true, float playTime = -1)
    {
        if (!Logged_AppIsPlaying()) return;
        
        if (emote == null)
        {
            Debug.LogWarning($"{GetType().Name} emote is not assigned, check inspector for invoked method field.");
            return;
        }
        if (user == null)
        {
            Debug.LogWarning($"{GetType().Name} user is not assigned, check inspector for invoked method field.");
            return;
        }

        InDataCommandCharacterEmote command = InDataCommandCharacterEmote.From(user.Id.GetValue(), toggle, emote.GetId(), playTime);
        Send(command);
    }
    
    [Button]
    public void SimulateClosestCharacterInProximityEmote(bool toggle = true, float playTime = -1)
    {
        if (!Logged_AppIsPlaying()) return;
        if (!Logged_GetRandomEmote(out SOEmote randomEmote)) return;

        SimulateClosestCharacterInProximityEmote(randomEmote, toggle);
    }

    [Button]
    public void SimulateClosestCharacterInProximityEmote(SOEmote emote, bool toggle = true, float playTime = -1)
    {
        if (!Logged_AppIsPlaying()) return;
        if (!Logged_GetPlayerCharacter(out CharacterEntity playerCharacter)) return;
        if (!Logged_GetCharacterNearByClosestOne(playerCharacter, CharacterPermission.Agent, out CharacterEntity closest)) return;
        
        Debug.Log($"Nearest: {closest.GetUser().Username.GetValue()}");
        
        SimulateCharacterEmote(emote, closest.GetUser(), toggle, playTime);
    }
    
    [Title("Summon")]
    [Button]
    public void SummonAgentNearPlayer()
    {
        if (!Logged_AppIsPlaying()) return;
        if (!Logged_GetPlayerCharacter(out CharacterEntity playerCharacter)) return;
        if (!Logged_GetRandomAvatar(out SOReadyPlayerMeAvatar randomAvatar)) return;

        Vector3 pos = playerCharacter.transform.position;
        Vector3 dir = UnityEngine.Random.onUnitSphere;
        dir.y = 0f;
        dir.Normalize();
        Vector3 targetPos = pos + (dir * _summonAgentRange.GetRandomInRange());

        Vector3 rot = (pos - targetPos).normalized;
        rot.y = 0f;
        rot.Normalize();
        Vector3 targetRot = Quaternion.LookRotation(rot).eulerAngles;

        
        InDataUser user = new()
        {
            id = GenerateRandomId(),
            username = _summonAgentNames.GetRandom()
        };

        InDataCharacter character = new()
        {
            modelPath = randomAvatar.GetUrl()
        };

        TransformData tr = new()
        {
            position = Vector3Data.FromVector3(targetPos),
            rotation = Vector3Data.FromVector3(targetRot)
        };

        InDataAgent agent = new()
        {
            user = user,
            character = character,
            transform = tr
        };

        InDataCommandSummonAgent command = InDataCommandSummonAgent.From(agent);
        Send(command);
    }

    [Button]
    public void SummonItem(SOItem soItem)
    {
        if (!Logged_AppIsPlaying()) return;

        if (soItem == null)
        {
            Debug.LogWarning("Item is null.");
            return;
        }

        if (!Logged_GetPlayerCharacter(out CharacterEntity playerCharacter)) return;

        InDataItem dataItem = new InDataItem
        {
            itemId = soItem.GetId(),
            transform = TransformData.From(playerCharacter.transform)
        };
        InDataCommandSummonItem command = InDataCommandSummonItem.From(dataItem);
        
        Send(command);
    }

    [Title("Movement")]
    
    [Button]
    public void MoveAllAgentsToRandomLocations()
    {
        if (!Logged_AppIsPlaying()) return;
        if (!Logged_GetCurrentGameLevel(out LyfeCreatorSceneData currentLevel)) return;
        
        List<AgentEntity> agentEntities = App.Instance.GetGame().GetAgents().GetAll();
        List<InDataCommand> commands = new List<InDataCommand>(agentEntities.Count);

        foreach (AgentEntity agentEntity in agentEntities)
        {
            if (!currentLevel.GetRandomArea(out LyfeCreatorWorldArea area))
            {
                Debug.LogWarning("Failed to find any random location areas in this game scene.");
                break;
            }

            InDataCommandAgentMoveDestinationLocation command = InDataCommandAgentMoveDestinationLocation.From(
                agentEntity.GetCharacter().GetUser().Id.GetValue(), area.GetKey());
            commands.Add(command);
        }
        Send(commands);
    }

    [Button]
    public void StopAllAgentMovement()
    {
        if (!Logged_AppIsPlaying()) return;
        if (!Logged_GetCurrentGameLevel(out LyfeCreatorSceneData currentLevel)) return;
        
        List<AgentEntity> agentEntities = App.Instance.GetGame().GetAgents().GetAll();
        List<InDataCommand> commands = new List<InDataCommand>(agentEntities.Count);
        
        foreach (AgentEntity agentEntity in agentEntities)
        {
            InDataCommandAgentMoveStop command = InDataCommandAgentMoveStop.From(agentEntity.GetCharacter().GetUser().Id.GetValue());
            commands.Add(command);
        }
        Send(commands);
    }

    [Title("Other")]
    
    [Button]
    public void LookAtPlayerClosestAgent()
    {
        if (!Logged_AppIsPlaying()) return;
        if (!Logged_GetPlayerCharacter(out CharacterEntity playerCharacter)) return;
        if (!Logged_GetCharacterNearByClosestOne(playerCharacter, CharacterPermission.Agent, out CharacterEntity closest)) return;

        InDataCommandCharacterLookAt command = InDataCommandCharacterLookAt.From(
            closest.GetUser().Id.GetValue(),
            playerCharacter.GetClient().GetSyncId());
        
        Send(command);
    }

    [Button]
    public void LookAtPlayerClearForAllClosest()
    {
        if (!Logged_AppIsPlaying()) return;
        if (!Logged_GetPlayerCharacter(out CharacterEntity playerCharacter)) return;

        HashSet<CharacterEntity> closests = playerCharacter.GetNearByCharacters().GetAllWithPermission(CharacterPermission.Agent);
        int count = closests.Count;

        if (count <= 0)
        {
            Debug.LogWarning("There are no near by agents.");
            return;
        }
        
        List<InDataCommand> commands = new List<InDataCommand>(count);
        foreach (CharacterEntity closest in closests) commands.Add(InDataCommandCharacterLookAtClear.From(closest.GetClient().GetSyncId()));
        Send(commands);
    }
    
    
    private void Send(InDataCommand command)
    {
        if (command == null)
        {
            Debug.LogWarning("Command null, skipping..");
            return;
        }
        Send(new []{command});
    }

    private void Send(InDataCommand[] commands)
    {
        if (commands == null || commands.Length <= 0)
        {
            Debug.LogWarning("Commands[] is null or empty, skipping..");
            return;
        }
        string json = CreateTaskJsonFromCommands(commands);
        Debug.Log(json);
        _python.ReceiveMessageFromPython(json);
    }

    private void Send(List<InDataCommand> commands) => Send(commands.ToArray());

    private string CreateTaskJsonFromCommands(InDataCommand[] commands)
    {
        PythonSendInTask task = CreateTaskFromCommands(commands);
        return JsonConvert.SerializeObject(task);
    }
    
    private PythonSendInTask CreateTaskFromCommands(InDataCommand[] commands)
    {
        return new()
        {
            messageType = PythonSendInMessageType.TASK,
            taskId = GenerateRandomId(),
            waitForResponse = false,
            commands = commands
        };
    }
    
    
    
    private string GenerateRandomId() => Guid.NewGuid().ToString();

    private bool Logged_GetRandomUser(out UserEntity user)
    {
        user = null;
        if (App.Instance.GetGame().GetCharacters().GetAll().GetRandom(out CharacterEntity character))
            user = character.GetUser();
        else
            Debug.LogWarning($"{GetType().Name} no random user found.");
        return user != null;
    }

    private bool Logged_GetRandomEmote(out SOEmote emote)
    {
        bool success = App.Instance.GetConfig().GetEmotes().GetRandomValue(out emote);
        if (!success)
            Debug.LogWarning($"{GetType().Name} no random emote found.");
        return success;
    }

    private bool Logged_AppIsPlaying()
    {
        if (!IsPlaying())
        {
            Debug.LogWarning("Simulating commands is allowed only in play mode.");
            return false;
        }
        return true;
    }

    private bool Logged_GetPlayerCharacter(out CharacterEntity playerCharacter)
    {
        if (!App.Instance.GetGame().GetPlayer().GetCharacter(out playerCharacter))
        {
            Debug.LogWarning("There is no active player character.");
            return false;
        }
        return true;
    }

    private bool Logged_GetCharacterNearByClosestOne(CharacterEntity characterEntity, CharacterPermission permission, out CharacterEntity closest)
    {
        closest = null;
        if (characterEntity == null)
        {
            Debug.LogWarning("Character is null.");
            return false;
        }
        if (!characterEntity.GetNearByCharacters().GetClosest(out closest, permission))
        {
            Debug.LogWarning("There are no near characters.");
            return false;
        }
        return true;
    }

    private bool Logged_GetCurrentGameLevel(out LyfeCreatorSceneData currentLevel)
    {
        if(!App.Instance.GetGame().GetCurrentLevel(out currentLevel))
        {
            Debug.LogWarning("There is currently no active game scene.");
            return false;
        }
        return true;
    }

    private bool Logged_GetRandomAvatar(out SOReadyPlayerMeAvatar randomAvatar)
    {
        if (!App.Instance.GetConfig().GetReadyPlayerMe().GetAvatars().GetRandomValue(out randomAvatar))
        {
            Debug.LogWarning("Failed to get random avatar model.");
            return false;
        }
        return true;
    }
}
