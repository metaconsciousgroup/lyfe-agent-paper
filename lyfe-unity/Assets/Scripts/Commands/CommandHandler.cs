using System;
using System.Collections;
using System.Linq;
using FishNet.Managing;
using UnityEngine;
using UnityEngine.Events;

public class CommandHandler : BaseMonoBehaviour
{
    [SerializeField] private bool _debug;
    [SerializeField] private SOAppConfig _config;
    private AppGame _game;
    private NetworkManager _networkManager;
    private AppEntitiesCharacters _characters;
    private AppAgents _agents;
    
    private SODebug GetDebug() => _config.GetEnvironment().GetDebugPython();

    /// <summary>
    /// Cached reference to game for faster access.
    /// </summary>
    /// <returns></returns>
    private AppGame GetGame()
    {
        if(_game == null) _game = App.Instance.GetGame();
        return _game;
    }

    /// <summary>
    /// Cached reference to network manager for faster access.
    /// </summary>
    /// <returns></returns>
    private NetworkManager GetNetworkManager()
    {
        if(_networkManager == null) _networkManager = GetGame().GetNetwork().GetNetworkManager();
        return _networkManager;
    }


    public AppEntities GetEntities() => GetGame().GetEntities();
    
    /// <summary>
    /// Cached reference to characters for faster access.
    /// </summary>
    /// <returns></returns>
    private AppEntitiesCharacters GetCharacters()
    {
        if (_characters == null) _characters = GetGame().GetCharacters();
        return _characters;
    }

    /// <summary>
    /// Cached reference to agents for faster access.
    /// </summary>
    /// <returns></returns>
    private AppAgents GetAgents()
    {
        if (_agents == null) _agents = GetGame().GetAgents();
        return _agents;
    }

    
    
    /// <summary>
    /// Processes commands.
    /// </summary>
    /// <param name="commands"></param>
    /// <param name="forceStopOnFailed">If true, on command execution failed all rest of the commands will be skipped.</param>
    /// <param name="onCompleted">Callback is fired for success and failed.</param>
    public void ExecuteCommands(InDataCommand[] commands, bool forceStopOnFailed, UnityAction<CommandResults> onCompleted)
    {
        int length = commands?.Length ?? 0;
        CommandResults results = new CommandResults(length);
        
        if (_debug)
        {
            string[] cmdTypes = commands == null ? Array.Empty<string>() : commands.Select(i => i.cmdType).ToArray();
            Debug.Log($"Executing {length} commands of types [{string.Join(", ", cmdTypes)}]");
        }
        
        // Invalid commands collection.
        if (commands == null)
        {
            results.countFailed++;
            onCompleted?.Invoke(results);
            return;
        }
        
        int index = 0;
        
        StartCoroutine(Handler());

        IEnumerator Handler()
        {
            // Iterate all commands and execute one by one with delayed completed callback.
            while (index < length)
            {
                
                InDataCommand command = commands[index];
                int resultIndex = index;
                bool isDone = false;
                
                // We must forcefully stop.
                if (results.skipped)
                {
                    results.array[resultIndex] = CommandResult.Skipped(command);
                    isDone = true;
                }
                else
                {
                    ExecuteRootCommand(command, OnCommandCompleted, OnCommandFailed);
                
                    // Command execution is success callback.
                    void OnCommandCompleted()
                    {
                        results.countSuccess++;
                        results.array[resultIndex] = CommandResult.Success(command);
                        isDone = true;
                        
                        if(_debug)
                            Debug.Log($"command {resultIndex + 1} / {length} Success [{command.cmdType}]");
                    }
                
                    // Command execution has failed callback.
                    void OnCommandFailed(ErrorData errorData)
                    {
                        CommandResult failResult = CommandResult.Failed(command, errorData);
                        
                        results.countFailed++;
                        results.array[resultIndex] = failResult;

                        // Command execution has failed and we should stop.
                        if (forceStopOnFailed) results.skipped = true;
                    
                        isDone = true;
                        
                        if(_debug)
                            Debug.LogWarning($"command {resultIndex} / {length} Failed [{command.cmdType}] reason: {failResult.errorData.message}");
                    }
                
                
                    // Wait for command to be done.
                    while (!isDone)
                    {
                        yield return null;
                    }
                }
                
                index++;
            }

            onCompleted?.Invoke(results);
        }
    }

    private void ExecuteRootCommand(InDataCommand command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        if (command == null)
        {
            onFailed?.Invoke(ErrorData.From("Command object is null."));
            return;
        }

        if (string.IsNullOrEmpty(command.cmdType))
        {
            onFailed?.Invoke(ErrorData.From("Command cmdType is null or empty."));
            return;
        }
        
        switch (command.cmdType)
        {
            case PythonCommandType.SCENE_LOAD:
            {
                ExecuteCommand((InDataCommandSceneLoad) command, onSuccess, onFailed);
                break;
            }
            case PythonCommandType.SUMMON_AGENT:
            {
                Debug.Log($"{GetType().Name} - ExecuteRootCommand - SUMMON_AGENT {command}");
                ExecuteCommand((InDataCommandSummonAgent) command, onSuccess, onFailed);
                break;
            }
            case PythonCommandType.SUMMON_ITEM:
            {
                Debug.Log($"{GetType().Name} - ExecuteRootCommand - SUMMON_ITEM {command}");
                ExecuteCommand((InDataCommandSummonItem) command, onSuccess, onFailed);
                break;
            }
            case PythonCommandType.CHARACTER_LOOK_AT:
            {
                ExecuteCommand((InDataCommandCharacterLookAt) command, onSuccess, onFailed);
                break;
            }
            case PythonCommandType.CHARACTER_LOOK_AT_CLEAR:
            {
                ExecuteCommand((InDataCommandCharacterLookAtClear) command, onSuccess, onFailed);
                break;
            }
            case PythonCommandType.CHARACTER_EMOTE:
            {
                ExecuteCommand((InDataCommandCharacterEmote) command, onSuccess, onFailed);
                break;
            }
            case PythonCommandType.AGENT_MOVE_DESTINATION_LOCATION:
            {
                ExecuteCommand((InDataCommandAgentMoveDestinationLocation) command, onSuccess, onFailed);
                break;
            }
            case PythonCommandType.AGENT_MOVE_DESTINATION_CHARACTER:
            {
                ExecuteCommand((InDataCommandAgentMoveDestinationCharacter) command, onSuccess, onFailed);
                break;
            }
            case PythonCommandType.AGENT_MOVE_STOP:
            {
                ExecuteCommand((InDataCommandAgentMoveStop) command, onSuccess, onFailed);
                break;
            }
            default:
            {
                onFailed?.Invoke(ErrorData.From($"Command type '{command.cmdType}' is not implemented"));
                break;
            }
        }
    }

    
    
    /// <summary>
    /// Load scene (Server-Only).
    /// </summary>
    /// <param name="command"></param>
    /// <param name="onSuccess"></param>
    /// <param name="onFailed"></param>
    private void ExecuteCommand(InDataCommandSceneLoad command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        GetGame().GetNetwork().LoadSceneOnServer(command.scene.name, OnSceneLoadCompleted, OnSceneLoadFailed);

        // Scene load on network completed
        void OnSceneLoadCompleted()
        {
            onSuccess?.Invoke();
        }

        // Scene load on network failed
        void OnSceneLoadFailed(ErrorData errorData)
        {
            onFailed?.Invoke(errorData);
        }
    }
    
    /// <summary>
    /// Summon agent.
    /// </summary>
    /// <param name="command"></param>
    /// <param name="onSuccess"></param>
    /// <param name="onFailed"></param>
    private void ExecuteCommand(InDataCommandSummonAgent command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        Debug.Log($"Summoning agent '{command.agent.user.username}'");
        AgentEntity agent = GetGame().CreateAgent(command.agent);
        GetNetworkManager().ServerManager.Spawn(agent.GetCharacter().gameObject);
        onSuccess?.Invoke();
    }
    
    /// <summary>
    /// Summon item.
    /// </summary>
    /// <param name="command"></param>
    /// <param name="onSuccess"></param>
    /// <param name="onFailed"></param>
    private void ExecuteCommand(InDataCommandSummonItem command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        GetGame().CreateItem(command.item, OnSuccess, onFailed);

        void OnSuccess(ItemEntity itemEntity)
        {
            GetNetworkManager().ServerManager.Spawn(itemEntity.gameObject);
            onSuccess?.Invoke();
        }
    }
    
    /// <summary>
    /// Set character look at target (Server-Only).
    /// </summary>
    /// <param name="command"></param>
    /// <param name="onSuccess"></param>
    /// <param name="onFailed"></param>
    private void ExecuteCommand(InDataCommandCharacterLookAt command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        // Find the character who will be looking
        if (!GetCharacters().GetById(command.userId, out CharacterEntity character))
        {
            string errorMessage = $"Look at character with user id '{command.userId.ToStringNullable()}' does not exist.";
            onFailed?.Invoke(ErrorData.From(errorMessage));
            return;
        }
        
        // Find the character we will be looking at
        if (!GetEntities().GetById(command.targetEntityId, out NetworkEntity networkEntity))
        {
            string errorMessage = $"Look at target entity with id '{command.targetEntityId.ToStringNullable()}' does not exist.";
            onFailed?.Invoke(ErrorData.From(errorMessage));
            return;
        }
        
        character.GetClient().FromServer_LookAtSet(networkEntity);
        onSuccess?.Invoke();
    }
    
    /// <summary>
    /// Clear character look at target (Server-Only).
    /// </summary>
    /// <param name="command"></param>
    /// <param name="onSuccess"></param>
    /// <param name="onFailed"></param>
    private void ExecuteCommand(InDataCommandCharacterLookAtClear command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        if (!GetCharacters().GetById(command.userId, out CharacterEntity character))
        {
            string errorMessage = $"Clear look at character with user id '{command.userId.ToStringNullable()}' does not exist.";
            onFailed?.Invoke(ErrorData.From(errorMessage));
            return;
        }
        
        character.GetClient().FromServer_LookAtClear();
        onSuccess?.Invoke();
    }
    
    /// <summary>
    /// Start or stop character emote.
    /// </summary>
    /// <param name="command"></param>
    /// <param name="onSuccess"></param>
    /// <param name="onFailed"></param>
    private void ExecuteCommand(InDataCommandCharacterEmote command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        if (!GetCharacters().GetById(command.userId, out CharacterEntity character))
        {
            onFailed?.Invoke(ErrorData.From("Could not found character with user id '{command.userId}'"));
            return;
        }

        if (!App.Instance.GetConfig().GetEmotes().GetById(command.emoteId, out SOEmote emote))
        {
            onFailed?.Invoke(ErrorData.From($"Emote with id '{command.emoteId}' does nto exist."));
            return;
        }

        if (character.ToggleEmote(emote, command.emoteActive, true, command.emotePlayTime))
        {
            onSuccess?.Invoke();
        }
        else
        {
            onFailed?.Invoke(ErrorData.From($"Failed to set emote '{emote.GetKind()}' state to: {command.emoteActive}"));
        }
    }
    
    /// <summary>
    /// Set agent move destination from location.
    /// </summary>
    /// <param name="command"></param>
    /// <param name="onSuccess"></param>
    /// <param name="onFailed"></param>
    private void ExecuteCommand(InDataCommandAgentMoveDestinationLocation command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        string agentId = command.agentId;
        string location = command.targetLocation;

        // Get current game level.
        if (!GetGame().GetCurrentLevel(out LyfeCreatorSceneData currentLevel))
        {
            string errorMessage = $"Navigation event agentId '{agentId.ToStringNullable()}' -> location '{location.ToStringNullable()}' received but current active game level does not exist.";
            Debug.LogWarning(errorMessage.Color(GetDebug().GetColor()));
            
            onFailed?.Invoke(ErrorData.From(errorMessage));
            return;
        }
        
        // Find agent by id.
        if (!GetAgents().GetAgentById(agentId, out AgentEntity agentEntity))
        {
            string errorMessage = $"Agent with id '{agentId.ToStringNullable()}' does not exist.";
            Debug.LogWarning(errorMessage.Color(GetDebug().GetColor()));
            
            onFailed?.Invoke(ErrorData.From(errorMessage));
            return;
        }

        // Get location destination.
        if (!currentLevel.GetAreaByKey(location, out LyfeCreatorWorldArea area))
        {
            string errorMessage = $"Navigation location '{location}' in current active game level does not exist.";
            Debug.LogWarning(errorMessage.Color(GetDebug().GetColor()));
            
            onFailed?.Invoke(ErrorData.From(errorMessage));
            return;
        }
        
        // Move character to destination
        NavigationPointWorld navigationPoint = NavigationPointWorld.From(area);
        agentEntity.SetMoveDestination(navigationPoint);
        onSuccess?.Invoke();
    }

    private void ExecuteCommand(InDataCommandAgentMoveDestinationCharacter command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        string agentId = command.agentId;
        string targetUserId = command.targetUserId;
        
        // Find agent by id.
        if (!GetAgents().GetAgentById(agentId, out AgentEntity agentEntity))
        {
            string errorMessage = $"Agent with id '{agentId.ToStringNullable()}' does not exist.";
            if(GetDebug().LogWarning)
                Debug.LogWarning(errorMessage.Color(GetDebug().GetColor()));
            
            onFailed?.Invoke(ErrorData.From(errorMessage));
            return;
        }

        // Find target user character
        if (!GetCharacters().GetById(targetUserId, out CharacterEntity targetCharacter))
        {
            string errorMessage = $"Follow target character with userId '{targetUserId.ToStringNullable()}' does not exist";
            if(GetDebug().LogWarning)
                Debug.LogWarning(errorMessage.Color(GetDebug().GetColor()));
            
            onFailed?.Invoke(ErrorData.From(errorMessage));
        }

        // Error - we are trying to follow ourselves
        if (agentEntity.GetCharacter() == targetCharacter)
        {
            string errorMessage = $"Set destination target character is our character - trying to follow themselves, this is not supported.";
            if(GetDebug().LogWarning)
                Debug.LogWarning(errorMessage.Color(GetDebug().GetColor()));
            
            onFailed?.Invoke(ErrorData.From(errorMessage));
        }
        
        NavigationPointCharacter navigationPoint = NavigationPointCharacter.From(targetCharacter);
        agentEntity.SetMoveDestination(navigationPoint);
        
        onSuccess?.Invoke();
    }

    private void ExecuteCommand(InDataCommandAgentMoveStop command, UnityAction onSuccess, UnityAction<ErrorData> onFailed)
    {
        string agentId = command.agentId;
        
        // Find agent by id.
        if (!GetAgents().GetAgentById(agentId, out AgentEntity agentEntity))
        {
            string errorMessage = $"Agent with id '{agentId.ToStringNullable()}' does not exist.";
            if(GetDebug().LogWarning)
                Debug.LogWarning(errorMessage.Color(GetDebug().GetColor()));
            
            onFailed?.Invoke(ErrorData.From(errorMessage));
            return;
        }

        agentEntity.StopMove();
        onSuccess?.Invoke();
    }

}
