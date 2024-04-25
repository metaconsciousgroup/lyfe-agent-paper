using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.SceneManagement;

public class AppGame : BaseMonoBehaviour
{
    [SerializeField] private SOAppConfig _config;
    [SerializeField] private Identifier _identifier;
    [SerializeField] private Player _player;
    [SerializeField] private AppAgents _agents;
    [SerializeField] private AppEntities _entities;
    [SerializeField] private AppUsers _users;
    [SerializeField] private AppNetwork _network;
    [Space]
    [SerializeField] private SceneLoader _sceneLoader;
    [SerializeField] private SOScene _sceneMainMenu;
    [Space]
    [ReadOnly, ShowInInspector] private PythonSendInGame _gameData;
    [ReadOnly, ShowInInspector] private UnityEventLoginRequest.Data _loginData;
    
    private HashIdGenerator _hashIdGenerator = new HashIdGenerator(16);

    public string GenerateId() => _hashIdGenerator.Generate();
    public AppAgents GetAgents() => _agents;
    public AppEntities GetEntities() => _entities;
    public AppEntitiesCharacters GetCharacters() => _entities.GetCharacters();
    public Player GetPlayer() => _player;
    public AppUsers GetUsers() => _users;
    public AppNetwork GetNetwork() => _network;
    public UnityEventLoginRequest.Data GetLoginData() => _loginData;
    public PythonSendInGame GetGameData() => _gameData;

    private SODebug GetDebug() => _config.GetEnvironment().GetDebugGame();

    private LyfeCreatorSceneData _currentLevel;

    /// <summary>
    /// Returns true if game contains current level.
    /// </summary>
    /// <returns></returns>
    public bool IsRunning() => _currentLevel != null;
    
    /// <summary>
    /// Returns true if game contains current level and have active player character.
    /// </summary>
    /// <returns></returns>
    public bool IsRunningAndHaveCharacter() => _currentLevel != null && _player.GetCharacter(out CharacterEntity character);

    public bool GetCurrentLevel(out LyfeCreatorSceneData value)
    {
        value = _currentLevel;
        return value != null;
    }

    public void UpdateCurrentLevel(Scene scene)
    {
        ClearCurrentLevel();

        if (!LyfeCreatorSceneData.Create(scene, _config.GetEnvironment().GetCreatorSettings(), out LyfeCreatorSceneData sceneData))
        {
            if (GetDebug().LogError)
                Debug.LogError("Failed to update current level".Color(GetDebug().GetColor()));
            return;
        }

        _currentLevel = sceneData;

        if (GetDebug().LogInfo)
            Debug.Log($"Current level updated: {_currentLevel}".Color(GetDebug().GetColor()));
    }

    public void ClearCurrentLevel()
    {
        if (_currentLevel == null) return;

        Destroy(_currentLevel.gameObject);
        _currentLevel = null;

        if (GetDebug().LogInfo)
            Debug.Log("Current level cleared".Color(GetDebug().GetColor()));
    }

    /// <summary>
    /// Called from AppNetwork inspector callback.
    /// </summary>
    public void OnAppNetworkClientConnectionStarted()
    {
        Login();
    }

    /// <summary>
    /// Called from AppNetwork inspector callback.
    /// </summary>
    public void OnAppNetworkClientConnectionFailed()
    {
        if (!GetNetwork().GetNetworkManager().IsServer)
        {
            LoadMainMenu(OnCompleted);

            void OnCompleted()
            {
                App.Instance.GetUI().GetView<UIViewInfoPopup>().Show(
                    "Error",
                    "Connection to server failed.",
                    InfoPopupButtonData.From("Close")
                );
            }
        }

    }

    /// <summary>
    /// Called from AppNetwork inspector callback.
    /// </summary>
    public void OnAppNetworkClientDisconnected()
    {
        if (!GetNetwork().GetNetworkManager().IsServer)
        {
            LoadMainMenu();
        }
    }

    public void OnUIViewChatPostMessage(string message, string channelId)
    {
        if (!_player.GetCharacter(out CharacterEntity playerCharacter))
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning("Cannot process player chat message, player is not initialized".Color(GetDebug().GetColor()));
            return;
        }

        if (GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.OnUIViewChatPostMessage: {message} for channel {channelId}".Color(GetDebug().GetColor()));

        playerCharacter.AddChatMessage(message, channelId);
    }

    /// <summary>
    /// Handles adding game chat message.
    /// </summary>
    /// <param name="chatMessageData"></param>
    /// <param name="character"></param>
    public void ShowChatMessage(ChatMessageData chatMessageData)
    {
        CharacterEntity authorCharacter = chatMessageData.author;

        // Add chat message to game chat for players
        App.Instance.GetUI().GetView<UIViewChat>().AddMessage(chatMessageData);

        if (chatMessageData.channelId == App.Instance.GetUI().GetView<UIViewChat>().GetDefaultChannelId())
        {
            // Add chat bubble for global message.
            App.Instance.GetUI().GetView<UIViewChatBubbles>().AddMessage(
                chatMessageData.message,
                authorCharacter.GetChatBubblePivot(),
                authorCharacter.GetUsernameRenderer().GetIdentifier(),
                true,
                out UIChatBubble chatBubble);
        }
    }

    public void ShowAgentMove(AgentMoveData agentMoveData, CharacterEntity displayToUser)
    {
        CharacterEntity agent = agentMoveData.agent;
        string leaveMessage = _config.GetLeaveForLocation().GetRandomReason(agentMoveData.locationName);
        ChatMessageData chatMessageData = ChatMessageData.From(agent, leaveMessage, App.Instance.GetUI().GetView<UIViewChat>().GetDefaultChannelId());
        // Reuse the chat bubble for now, but we need to create a new one for thought bubble.
        App.Instance.GetUI().GetView<UIViewChat>().AddMessage(chatMessageData);
        App.Instance.GetUI().GetView<UIViewChatBubbles>().AddMessage(
            leaveMessage,
            agent.GetChatBubblePivot(),
            agent.GetUsernameRenderer().GetIdentifier(),
            true,
            out UIChatBubble chatBubble);
    }

    public void OnWebsocketGameInitialized(PythonSendInGame value)
    {
        Debug.Log($"OnWebsocketGameInitialized: {value}");
        OnSendInGame(value);
    }

    public void OnAppPythonGameDataInitialized(PythonSendInGame value)
    {
        OnSendInGame(value);
    }
    private void OnSendInGame(PythonSendInGame value)
    {
        _gameData = value;
        UIViewLobbyHost viewLobby = App.Instance.GetUI().GetView<UIViewLobbyHost>();
        viewLobby.SetData(value);

        switch (App.Instance.GetConfig().GetEnvironment().GetKind())
        {
            case AppKind.Development:
                {
                    viewLobby.ToggleGroup(true);
                    break;
                }
            case AppKind.Server:
                {
                    viewLobby.OnButtonStart();
                    break;
                }
        }
    }

    /// <summary>
    /// Starts game as a host.
    /// </summary>
    /// <param name="data"></param>
    public void StartHost(UnityEventLoginRequest.Data data)
    {
        if (_gameData == null)
        {
            if (GetDebug().LogError)
                Debug.LogError("Cant start host, game data is not initialized".Color(GetDebug().GetColor()));
            return;
        }

        if (GetDebug().LogInfo)
            Debug.Log($"Starting host: {data}");
        InternalSharedNetworkWarmup(data);
        _network.StartServer();
    }

    /// <summary>
    /// Starts game as a client.
    /// </summary>
    /// <param name="data"></param>
    public void StartClient(UnityEventLoginRequest.Data data)
    {
        if (GetDebug().LogInfo)
            Debug.Log($"Starting client: {data}".Color(GetDebug().GetColor()));

        InternalSharedNetworkWarmup(data);
        _network.StartClient();
    }

    private void InternalSharedNetworkWarmup(UnityEventLoginRequest.Data data)
    {
        _loginData = data;

        _network.SetNetwork(data.networkAddress, data.portStandalone, data.portWeb);
    }



    public AgentEntity[] CreateAgents(InDataAgent[] value)
    {
        if (value == null) return null;
        int length = value.Length;
        AgentEntity[] entities = new AgentEntity[length];

        for (int i = 0; i < length; i++)
        {
            entities[i] = CreateAgent(value[i]);
        }
        return entities;
    }

    public AgentEntity CreateAgent(InDataAgent dataAgent)
    {
        CharacterEntity character = _entities.GetCharacters().Create(dataAgent);
        AgentEntity agent = _agents.Create(character);

        agent.SetData(dataAgent);
        character.SetupAsAgent(true);

        return agent;
    }

    public void CreateItem(InDataItem dataItem, UnityAction<ItemEntity> onSuccess = null, UnityAction<ErrorData> onFailed = null)
    {
        if (dataItem == null)
        {
            onFailed?.Invoke(ErrorData.From("Data is null."));
            return;
        }
        
        string itemId = dataItem.itemId;
            
        if (!_config.GetItems().GetByName(itemId, out SOItem soItem))
        {
            onFailed?.Invoke(ErrorData.From($"Failed to find item by id '{itemId.ToStringNullable()}'."));
            return;
        }

        ItemEntity prefab = soItem.GetPrefab();
        
        if (prefab == null)
        {
            onFailed?.Invoke(ErrorData.From($"Item '{itemId}' prefab is null."));
            return;
        }

        TransformData tr = dataItem.transform;
        ItemEntity itemEntity = Instantiate(prefab, _entities.GetItems().transform);
        itemEntity.transform.position = tr.position.GetVector3();
        itemEntity.transform.rotation = Quaternion.Euler(tr.rotation.GetVector3());
        itemEntity.SetSyncId(GenerateId());
        Debug.Log($"Summoned item '{itemId}'");
        
        onSuccess?.Invoke(itemEntity);
    }

    /// <summary>
    /// Requests client login authentication.
    /// </summary>
    private void Login()
    {
        UnityEventLoginRequest.Data ld = App.Instance.GetGame().GetLoginData();

        FishNetAuthenticator.AuthRequest request = new FishNetAuthenticator.AuthRequest()
        {
            username = ld.username,
            characterModelPath = ld.character.modelPath
        };

        GetNetwork().GetAuthenticator().Authenticate(request);
    }

    /// <summary>
    /// Loads main menu scene.
    /// This takes into consideration current app config, and switches starting ui view depending on environment Client, Server or Development.
    /// </summary>
    public void LoadMainMenu(UnityAction onCompleted = null)
    {
        if (GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.LoadMainMenu(): {_config.GetEnvironment().GetKind()}".Color(GetDebug().GetColor()));

        App.Instance.GetUI().CloseAllViews();
        _sceneLoader.LoadSceneAsync(_sceneMainMenu.GetName(), LoadSceneMode.Single, true, null, null, OnSceneLoadCompleted, OnSceneLoadFailed);

        void OnSceneLoadCompleted(Scene scene)
        {
            if (GetDebug().LogInfo)
                Debug.Log($"Loaded scene '{scene.name}'".Color(GetDebug().GetColor()));
            
            // Move camera to main menu camera pivot
            SceneMainMenu mainMenu = scene.GetRootGameObjects().GetComponentPro<SceneMainMenu>();
            if (mainMenu != null)
            {
                _player.GetCamera().SetCustomPosition(mainMenu.GetCameraPivot());
            }
            

            switch (_config.GetEnvironment().GetKind())
            {
                case AppKind.Development:
                    {
                        App.Instance.GetUI().GetView<UIViewAppEnvironment>().OpenGroup();
                        break;
                    }
                case AppKind.Server:
                    {
                        StartAsServer();
                        break;
                    }
                case AppKind.Client:
                    {
                        StartAsClient();
                        break;
                    }
            }
            onCompleted?.Invoke();
        }

        void OnSceneLoadFailed(string error)
        {
            Debug.LogError(error);
        }
    }

    public void UnloadMainMenu(UnityAction onCompleted = null, UnityAction<string> onFailed = null)
    {
        _sceneLoader.UnloadSceneAsync(_sceneMainMenu.GetName(), null, null, OnSceneLoadCompleted, OnSceneLoadFailed);
        
        void OnSceneLoadCompleted()
        {
            onCompleted?.Invoke();
        }

        void OnSceneLoadFailed(string error)
        {
            Debug.LogError(error);
            onFailed?.Invoke(error);
        }
    }

    public void StartAsServer()
    {
        App.Instance.GetUI().CloseAllViewsExcept<UIViewLobbyHost>();
        App.Instance.GetPythonWebSocket().Initialize(_config.GetEnvironment().forcePythonConnection);
    }

    public void StartAsClient()
    {
        App.Instance.GetUI().CloseAllViewsExcept<UIViewLobbyClient>();
    }

}
