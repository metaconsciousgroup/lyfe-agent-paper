using System;
using System.Collections;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using System.Linq;

/// <summary>
/// Handles python initialization, incoming and outgoing messaging.
/// </summary>
public abstract class AppPython : BaseMonoBehaviour
{
    [Title("Python")]
    [Tooltip("Python initialization flag.")]
    [ReadOnly, ShowInInspector] private bool _isInitialized;
    [ReadOnly, ShowInInspector] private bool _isGameDataInitialized;
    [SerializeField] private CommandHandler _commandHandler;
    [SerializeField] private AppPythonGameEventHandler _gameEventHandler;
    [SerializeField] private PythonCommandSimulator _commandSimulator;
    [Space]
    [SerializeField] private UnityEvent<PythonSendInGame> _onGameDataInitialized;

    
    protected SODebug GetDebug() => App.Instance.GetConfig().GetEnvironment().GetDebugPython();
    public PythonCommandSimulator GetCommandSimulator() => _commandSimulator;

    public bool GetConfig(out SOPython config)
    {
        config = App.Instance.GetConfig().GetEnvironment().GetPython();
        return config != null;
    }

    /// <summary>
    /// Initializes python connections and processing.
    /// </summary>
    /// <param name="forceConnection">If true, game will not proceed until establishing python connection.</param>
    public void Initialize(bool forceConnection)
    {
        if (_isInitialized)
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning("Already initialized".Color(GetDebug().GetColor()));
            return;
        }
        _isInitialized = true;

        if (forceConnection)
        {
            StartCoroutine(InitializeConnection());
        }
        else
        {
            Initialize_Internal();
        }
    }

    protected abstract IEnumerator InitializeConnection();
    protected abstract void Initialize_Internal_Subclass();
    protected abstract void SendToPython_Internal(string message);

    protected void Initialize_Internal()
    {
        if (GetDebug().LogInfo)
            Debug.Log($"{GetType()}.Initialize_Internal".Color(GetDebug().GetColor()));

        Initialize_Internal_Subclass();
        _gameEventHandler.ListenGameEvents(true);

        StartCoroutine(PythonUpdate());
        WaitAndInitializeFallbackGameData();
    }

    public void SendToPython(PythonSendOut value)
    {
        if (!_isInitialized)
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning($"{GetType().Name}.SendToPython: {value.messageType} skipped, python not initialized".Color(GetDebug().GetColor()));
            return;
        }

        if (GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.SendToPython: {value.messageType}".Color(GetDebug().GetColor()));

        string json = JsonConvert.SerializeObject(value, new JsonSerializerSettings
        {
            Converters = new List<JsonConverter> { new StringEnumConverter() }
        });
        SendToPython_Internal(json);
    }

    private IEnumerator PythonUpdate()
    {
        while (_isInitialized && IsPlaying())
        {
            if (_isGameDataInitialized)
            {
                SendToPython(PythonSendOutCharacterProximity.From(App.Instance.GetGame()));
            }

            yield return new WaitForSeconds(0.2f);
        }
    }

    private void OnAppGamePlayerDirectMessage(ChatMessageData chatMessageDataDirect)
    {
        string message = chatMessageDataDirect.message;
        string channelId = chatMessageDataDirect.channelId;
        string[] locations = chatMessageDataDirect.author.GetNearByAreas().GetAll().Select<LyfeCreatorWorldArea, string>(i => i.GetKey()).ToArray();

        if (App.Instance.GetGame().GetPlayer().GetCharacter(out CharacterEntity character))
        {
            string playerId = character.GetUser().Id.GetValue();

            if (GetDebug().LogInfo)
                Debug.Log($"AppPython OnAppGamePlayerDirectMessage  message[{message}] to receiverId[{channelId}]".Color(GetDebug().GetColor()));

            // Check if the receiverId corresponds to an agent
            if (GetAgentById(channelId, out AgentEntity receiverAgentEntity))
            {
                // Send chat message back to Python since it's an agent
                SendToPython(new PythonSendOutPlayerDirectMessage(playerId, channelId, message, locations));
            }
        }
    }

    public void ReceiveMessageFromPython(string message)
    {
        if (GetDebug().LogInfo)
            Debug.Log($"{GetType()} received: {message}");

        // Parse message from Python. Message type must be inherited from PythonSendIn
        PythonSendIn sendIn = JsonConvert.DeserializeObject<PythonSendIn>(message);
        string messageType = sendIn.messageType;

        if (string.IsNullOrEmpty(messageType))
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning($"{nameof(PythonSendIn)}.messageType is null or empty".Color(GetDebug().GetColor()));
            return;
        }

        switch (messageType)
        {
            case PythonSendInMessageType.TASK:
                {
                    OnPythonHandler(JsonConvert.DeserializeObject<PythonSendInTask>(message));
                    break;
                }
            case PythonSendInMessageType.GAME_DATA:
            {
                    PythonSendInGame data = JsonConvert.DeserializeObject<PythonSendInGame>(message);
                    data.fromPython = true;
                    OnPythonHandler(data);
                    break;
                }
            case PythonSendInMessageType.AGENT_CHAT_MESSAGE:
                {
                    OnPythonHandler(JsonConvert.DeserializeObject<PythonSendInAgentChatMessage>(message));
                    break;
                }
            case PythonSendInMessageType.AGENT_DIRECT_MESSAGE:
                {
                    OnPythonHandler(JsonConvert.DeserializeObject<PythonSendInAgentDirectMessage>(message));
                    break;
                }
            case PythonSendInMessageType.AGENT_MOVE_DESTINATION_LOCATION:
                {
                    OnPythonHandler(JsonConvert.DeserializeObject<PythonSendInAgentMoveDestinationLocation>(message));
                    break;
                }
            case PythonSendInMessageType.OBJECT_INSTANTICATION:
                {
                    OnPythonHandler(JsonConvert.DeserializeObject<PythonSendInObjectInstantiationMessage>(message));
                    break;
                }
            default:
                {
                    if (GetDebug().LogError)
                        Debug.LogError($"Failed to resolve python messageType: {messageType}".Color(GetDebug().GetColor()));
                    break;
                }
        }
    }

    private void OnPythonHandler(PythonSendInTask task)
    {
        if (GetDebug().LogInfo)
            Debug.Log($"Received task: {task.taskId} with {task.commands.Length} commands".Color(GetDebug().GetColor()));
        
        _commandHandler.ExecuteCommands(task.commands, true, OnCompleted);

        void OnCompleted(CommandResults results)
        {
            if (GetDebug().LogInfo)
                Debug.Log($"Task {task.taskId} completed with {results.success}".Color(GetDebug().GetColor()));
            
            // All commands executed with success
            if (results.success)
            {
                // We should respond to python about our success
                if (task.waitForResponse)
                {
                    SendToPython(new PythonSendOutTaskCompleted(task.taskId, results));
                }
            }
            // One or many commands failed - notify python
            else
            {
                SendToPython(new PythonSendOutTaskCompleted(task.taskId, results));
            }
        }
    }


    private void OnPythonHandler(PythonSendInGame data)
    {
        // Process game data
        SetGameData(data, true);
    }

    /// <summary>
    /// Process agent chat message. Chat message is sent to all nearby players and agents.
    /// </summary>
    /// <param name="data"></param>
    private void OnPythonHandler(PythonSendInAgentChatMessage data)
    {
        if (!GetAgentById(data.agentId, out AgentEntity agentEntity))
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning($"Agent with id '{data.agentId.ToStringNullable()}' does not exist".Color(GetDebug().GetColor()));
            return;
        }

        agentEntity.GetCharacter().AddChatMessage(data.message);
    }

    private void OnPythonHandler(PythonSendInAgentDirectMessage data)
    {
        // Process agent direct message. Direct message is sent to a specific player or agent
        // agentEntity is the sender
        if (!GetAgentById(data.agentId, out AgentEntity senderAgentEntity))
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning($"Agent with id '{data.agentId.ToStringNullable()}' does not exist".Color(GetDebug().GetColor()));
        }

        // Extract the receiver ID and message from the DirectMessage data
        string receiverId = data.receiverId;
        string message = data.message;

        // Check if the receiver is a player. If a player, then send direct message to player.
        // If receiver is an agent, then send direct message to agent through Python
        // Check if the receiverId corresponds to an agent
        if (GetAgentById(receiverId, out AgentEntity receiverAgentEntity))
        {
            string[] locations = receiverAgentEntity.GetCharacter().GetNearByAreas().GetAll().Select<LyfeCreatorWorldArea, string>(i => i.GetKey()).ToArray();
            // Send chat message back to Python since it's an agent
            SendToPython(new PythonSendOutAgentDirectMessage(data.agentId, receiverId, message, locations));
        }
        // Check if receiverId corresponds to a player
        else if (GetCharacterById(receiverId, out CharacterEntity receiverPlayerEntity))
        {
            // Send direct chat message to player
            senderAgentEntity.GetCharacter().AddDirectChatMessage(message, receiverPlayerEntity);
        }
        // Neither a player nor an agent
        else
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning($"Receiver with id '{receiverId}' does not exist".Color(GetDebug().GetColor()));
        }
    }

    private void OnPythonHandler(PythonSendInAgentMoveDestinationLocation data)
    {
        // Process agent move destination location. Move agent to destination location (string)
        if (!GetAgentById(data.agentId, out AgentEntity agentEntity))
        {
            if (GetDebug().LogWarning)
            {
                Debug.LogWarning($"Agent with id '{data.agentId.ToStringNullable()}' does not exist".Color(GetDebug().GetColor()));
                return;
            }
        }

        string location = data.location;

        if (!App.Instance.GetGame().GetCurrentLevel(out LyfeCreatorSceneData currentLevel))
        {
            if (GetDebug().LogError)
            {

                Debug.LogError($"Navigation event '{location}' received but level is not loaded".Color(GetDebug().GetColor()));
                return;
            }

        }

        // Try to get destination by target location name
        if (currentLevel.GetAreaByKey(location, out LyfeCreatorWorldArea area))
        {
            // Debug.LogWarning($"Navigation destination '{location}' in level does not exist");
            // Move character to destination
            NavigationPointWorld navigationPoint = NavigationPointWorld.From(area);
            agentEntity.SetMoveDestination(navigationPoint);
            agentEntity.GetCharacter().BroadcastAgentMove(AgentMoveData.From(agentEntity.GetCharacter(), location));
            return;
        }

        if (GetDebug().LogInfo)
            Debug.Log($"Trying to navigate to agent {location}".Color(GetDebug().GetColor()));

        // Try to navigate to location of agents
        List<CharacterEntity> characters = App.Instance.GetGame().GetCharacters().GetAll();

        // Loop over all characters
        foreach (CharacterEntity characterEntity in characters)
        {
            // Check if character is at location
            if (GetDebug().LogInfo)
                Debug.Log($"Checking if {characterEntity.GetUsernameRenderer().GetUsername()} is destination".Color(GetDebug().GetColor()));

            if (characterEntity.GetUsernameRenderer().GetUsername().Equals(location))
            {
                NavigationPointCharacter navigationPoint = NavigationPointCharacter.From(characterEntity);
                // Move character to destination
                agentEntity.SetMoveDestination(navigationPoint);
                return;
            }
        }

    }

    private void OnPythonHandler(PythonSendInObjectInstantiationMessage data)
    {
        String objectType = data.objectType;
        if (String.IsNullOrEmpty(objectType) || !(objectType.Equals("Sphere") || objectType.Equals("Cube")))
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning($"Object type '{objectType}' is not supported".Color(GetDebug().GetColor()));
        }
        // Check if the Agent exists
        if (!GetAgentById(data.agentId, out AgentEntity agentEntity))
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning($"Agent with id '{data.agentId.ToStringNullable()}' does not exist".Color(GetDebug().GetColor()));
        }

        if (GetDebug().LogInfo)
            Debug.Log($"Agent id: '{data.agentId}' is instantiating object of type: '{objectType}'".Color(GetDebug().GetColor()));

        if (objectType.Equals("Sphere"))
        {
            // Instantiate a sphere with the transform data relative to the agent
            GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sphere.transform.SetPositionAndRotation(agentEntity.GetCharacter().transform.position + data.transform.position.GetVector3(), Quaternion.Euler(data.transform.rotation.GetVector3()));
            sphere.name = agentEntity.GetCharacter().GetUsernameRenderer().GetUsername() + "'s Sphere";
        }
        else if (objectType.Equals("Cube"))
        {
            // Instantiate a cube with the transform data relative to the agent
            GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cube.transform.SetPositionAndRotation(agentEntity.GetCharacter().transform.position + data.transform.position.GetVector3(), Quaternion.Euler(data.transform.rotation.GetVector3()));
            cube.name = agentEntity.GetCharacter().GetUsernameRenderer().GetUsername() + "'s Cube";
        }

    }

    private bool GetAgentById(string agentId, out AgentEntity agentEntity)
    {
        return App.Instance.GetGame().GetAgents().GetAgentById(agentId, out agentEntity);
    }

    private bool GetCharacterById(string playerId, out CharacterEntity character)
    {
        return App.Instance.GetGame().GetCharacters().GetById(playerId, out character);
    }


    private void WaitAndInitializeFallbackGameData()
    {
        // Probably already initialized from python
        if (_isGameDataInitialized) return;
        
        if (!GetConfig(out SOPython config))
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning("Missing python config, skipping..".Color(GetDebug().GetColor()));
            return;
        }

        if (!config.GetFallbackData(out PythonSendInGame fallback))
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning("Missing python fallback data, skipping..".Color(GetDebug().GetColor()));
            return;
        }

        if (config.ForceFallback())
        {
            SetGameData(fallback, false);
            return;
        }

        StartCoroutine(Handler());

        IEnumerator Handler()
        {
            yield return new WaitForSeconds(config.GetInitWaitTime());
            SetGameData(fallback, false);
        }
    }

    /**
     * You can only set this once.
     */
    private void SetGameData(PythonSendInGame value, bool fromPython)
    {
        if (_isGameDataInitialized) return;
        _isGameDataInitialized = true;

        if (GetDebug().LogInfo)
            Debug.Log($"{GetType()} game data initialized from {(fromPython ? "PYTHON" : "FALLBACK")}".Color(GetDebug().GetColor()));

        _onGameDataInitialized.Invoke(value);
    }

}
