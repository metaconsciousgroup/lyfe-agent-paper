using System.Collections.Generic;
using System.Linq;
using FishNet.Connection;
using FishNet.Managing;
using FishNet.Managing.Client;
using FishNet.Managing.Scened;
using FishNet.Managing.Server;
using FishNet.Object;
using FishNet.Transporting;
using FishNet.Transporting.Bayou;
using FishNet.Transporting.Multipass;
using FishNet.Transporting.Tugboat;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.SceneManagement;
using SceneManager = FishNet.Managing.Scened.SceneManager;

public class AppNetwork : BaseMonoBehaviour
{
    [Header(H_L + "FishNet" + H_R)]
    [SerializeField] private NetworkManager _networkManager;
    [SerializeField] private Tugboat _transportTugboat;
    [SerializeField] private Bayou _transportBayou;
    [Space]
    [SerializeField] private SOAppConfig _config;
    [ReadOnly, ShowInInspector] private NetworkData _defaultNetworkOverrides = new NetworkData();
    [Space]
    [SerializeField] private NetworkObject _playerPrefab;
    [Tooltip("Current state of server socket.")]
    [ReadOnly, ShowInInspector] private LocalConnectionState _stateServer = LocalConnectionState.Stopped;
    [Tooltip("Current state of client socket.")]
    [ReadOnly, ShowInInspector] private LocalConnectionState _stateClient = LocalConnectionState.Stopped;
    [SerializeField] private UnityEventSceneLoadStartEventArgs _onSceneManagerLoadStart;
    [SerializeField] private UnityEventSceneLoadPercentEventArgs _onSceneManagerLoadPercentChange;
    [SerializeField] private UnityEventSceneLoadEndEventArgs _onSceneManagerLoadEnd;
    [Space]
    [SerializeField] private UnityEvent<ClientNetworkBehaviour> _onServerClientAdded;
    [SerializeField] private UnityEvent<ClientNetworkBehaviour> _onServerClientRemoved;
    [SerializeField] private UnityEvent<ChatMessageData> _onChatMessageProcessed;
    [SerializeField] private UnityEvent<AgentMoveData> _onAgentMoveProcessed;
    [Space]
    [SerializeField] private UnityEvent _onServerStarted;
    [Space]
    [SerializeField] private UnityEvent _onClientConnectionStarted;
    [SerializeField] private UnityEvent _onClientConnectionFailed;
    [SerializeField] private UnityEvent _onClientDisconnected;

    private bool _isClientConnected;

    [ReadOnly, ShowInInspector]
    private SceneLoadEvent _serverLoadSceneProcess = null;
    
    
    public UnityEvent onServerStarted => _onServerStarted??= new UnityEvent();

    public bool IsServerLoadingScene() => _serverLoadSceneProcess != null;
    

    private class SceneLoadEvent
    {
        public readonly string sceneName;
        public readonly UnityEvent onCompleted = new();
        public readonly UnityEvent<ErrorData> onFailed = new();

        public SceneLoadEvent(string sceneName, UnityAction onCompleted, UnityAction<ErrorData> onFailed)
        {
            this.sceneName = sceneName;
            if(onCompleted != null) this.onCompleted.AddListener(onCompleted);
            if(onFailed != null) this.onFailed.AddListener(onFailed);
        }
    }


    public UnityEvent<ClientNetworkBehaviour> onServerClientAdded => _onServerClientAdded;
    public UnityEvent<ClientNetworkBehaviour> onServerClientRemoved => _onServerClientRemoved;
    public NetworkManager GetNetworkManager() => _networkManager;
    public UnityEvent<ChatMessageData> onChatMessageProcessed => _onChatMessageProcessed;
    public UnityEvent<AgentMoveData> onAgentMoveProcessed => _onAgentMoveProcessed;
    
    private bool _agentsInitialized = false;

    [ReadOnly, ShowInInspector]
    private Dictionary<LocalConnectionState, HashSet<int>> _serverManagerTransportStates = new();

    public Multipass GetMultipass() => _networkManager.TransportManager.GetTransport<Multipass>();

    public FishNetAuthenticator GetAuthenticator() => (FishNetAuthenticator)_networkManager.ServerManager.GetAuthenticator();

    public NetworkData GetDefaultNetworkOverrides() => _defaultNetworkOverrides;
    
    private SODebug GetDebug() => _config.GetEnvironment().GetDebugNetwork();

    /// <summary>
    /// Returns global network defaults.
    /// </summary>
    /// <returns></returns>
    public NetworkData GetNetworkDefaults()
    {
        NetworkData config = _config.GetEnvironment().GetNetwork();
        NetworkData over = _defaultNetworkOverrides;

        string hostname = string.IsNullOrEmpty(over.hostName) ? config.hostName : over.hostName;
        string portStandAlone = string.IsNullOrEmpty(over.portStandalone) ? config.portStandalone : over.portStandalone;
        string portWeb = string.IsNullOrEmpty(over.portWeb) ? config.portWeb : over.portWeb;
        string username = string.IsNullOrEmpty(over.username) ? config.username : over.username;

        return new NetworkData(hostname, portStandAlone, portWeb, username);
    }


    protected override void Start()
    {
        base.Start();
        RegisterToFishNetEvents(true);
    }

    protected override void OnDestroy()
    {
        base.OnDestroy();
        RegisterToFishNetEvents(false);
    }

    private void RegisterToFishNetEvents(bool alter)
    {
        if (_networkManager == null) return;
        ServerManager serverManager = _networkManager.ServerManager;
        ClientManager clientManager = _networkManager.ClientManager;
        SceneManager sceneManager = _networkManager.SceneManager;

        if (serverManager == null || clientManager == null || sceneManager == null)
        {
            if(GetDebug().LogError)
                Debug.LogError("Altering fish net event subscriptions skipped.".Color(GetDebug().GetColor()));
            return;
        }

        if (alter)
        {
            // Server
            serverManager.OnServerConnectionState += ServerManager_OnServerConnectionState;
            serverManager.OnClientKick += ServerManager_OnClientKick;
            serverManager.OnAuthenticationResult += ServerManager_OnAuthenticationResult;
            serverManager.OnRemoteConnectionState += ServerManager_OnRemoteConnectionState;

            // Client
            clientManager.OnClientConnectionState += ClientManager_OnClientConnectionState;
            clientManager.OnAuthenticated += ClientManager_OnAuthenticated;

            // Scene
            sceneManager.OnClientLoadedStartScenes += SceneManager_OnClientLoadedStartScenes;
            sceneManager.OnLoadStart += SceneManager_OnLoadStart;
            sceneManager.OnLoadPercentChange += SceneManager_OnLoadPercentChange;
            sceneManager.OnLoadEnd += SceneManager_OnLoadEnd;
        }
        else
        {
            // Server
            serverManager.OnServerConnectionState -= ServerManager_OnServerConnectionState;
            serverManager.OnClientKick -= ServerManager_OnClientKick;
            serverManager.OnAuthenticationResult -= ServerManager_OnAuthenticationResult;
            serverManager.OnRemoteConnectionState -= ServerManager_OnRemoteConnectionState;

            // Client
            clientManager.OnClientConnectionState -= ClientManager_OnClientConnectionState;
            clientManager.OnAuthenticated -= ClientManager_OnAuthenticated;

            // Scene
            sceneManager.OnClientLoadedStartScenes -= SceneManager_OnClientLoadedStartScenes;
            sceneManager.OnLoadStart -= SceneManager_OnLoadStart;
            sceneManager.OnLoadPercentChange -= SceneManager_OnLoadPercentChange;
            sceneManager.OnLoadEnd -= SceneManager_OnLoadEnd;
        }
    }

    /// <summary>
    /// Called after the local server connection state changes.
    /// Note that this is called for each separate transport!
    /// </summary>
    /// <param name="obj"></param>
    private void ServerManager_OnServerConnectionState(ServerConnectionStateArgs obj)
    {
        UpdateServerManagerTransportState(obj.TransportIndex, obj.ConnectionState);

        _stateServer = obj.ConnectionState;

        switch (obj.ConnectionState)
        {
            case LocalConnectionState.Started:
                {
                    if (CheckAllTransportState(LocalConnectionState.Started))
                    {
                        if(GetDebug().LogInfo)
                            Debug.Log("All server transports initialized".Color(GetDebug().GetColor()));
                        OnServerStarted();
                    }
                    break;
                }
        }
    }

    /// <summary>
    /// Called when all server transports have initialized.
    /// </summary>
    private void OnServerStarted()
    {
        App.Instance.GetUI().GetView<UIViewServer>().ToggleGroup(true);

        if(GetDebug().LogInfo)
            Debug.Log($"{nameof(AppNetwork)}.OnServerStarted".Color(GetDebug().GetColor()));
        
        _onServerStarted.Invoke();
    }

    public void LoadSceneOnServer(string sceneName, UnityAction onCompleted, UnityAction<ErrorData> onFailed)
    {
        // Server is already loading scene!
        if (IsServerLoadingScene())
        {
            onFailed?.Invoke(ErrorData.From("Server load scene already in progress"));
            return;
        }
        
        SceneLoadData sld = new SceneLoadData(sceneName)
        {
            Options =
            {
                Addressables = true
            }
        };

        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.LoadSceneOnServer({sceneName})".Color(GetDebug().GetColor()));
        _serverLoadSceneProcess = new SceneLoadEvent(sceneName, onCompleted, onFailed);
        _networkManager.SceneManager.LoadGlobalScenes(sld);
    }

    /// <summary>
    /// Returns true if all multipass transports have started.
    /// </summary>
    /// <returns></returns>
    private bool CheckAllTransportState(LocalConnectionState localConnectionState)
    {
        return GetServerManagerTransportStateCount(localConnectionState) == GetMultipass().Transports.Count;
    }

    private void UpdateServerManagerTransportState(int transportIndex, LocalConnectionState state)
    {
        // Remove from all
        foreach (var keyValuePair in _serverManagerTransportStates)
        {
            keyValuePair.Value.Remove(transportIndex);
        }

        // Add
        HashSet<int> set;

        if (_serverManagerTransportStates.TryGetValue(state, out HashSet<int> transportIndexSet))
        {
            set = transportIndexSet;
        }
        else
        {
            set = new HashSet<int>();
            _serverManagerTransportStates.Add(state, set);
        }

        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on server connection state changed for transportIndex'{transportIndex}' '{state}'".Color(GetDebug().GetColor()));
        set.Add(transportIndex);
    }

    private int GetServerManagerTransportStateCount(LocalConnectionState state)
    {
        if (!_serverManagerTransportStates.ContainsKey(state)) return 0;
        return _serverManagerTransportStates[state].Count;
    }

    /// <param name="networkConnection">NetworkConnection when available.</param>
    /// <param name="clientId">Client id.</param>
    /// <param name="reason">Kick reason.</param>
    private void ServerManager_OnClientKick(NetworkConnection networkConnection, int clientId, KickReason reason)
    {
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on server client kick connection[{_stateServer}] clientId[{clientId}] reason[{reason}]".Color(GetDebug().GetColor()));
    }

    /// <param name="connection">Client connection.</param>
    /// <param name="success">Boolean is true if authentication passed, false if failed.</param>
    private void ServerManager_OnAuthenticationResult(NetworkConnection connection, bool success)
    {
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on server authentication result connection[{connection}] success[{success}]'".Color(GetDebug().GetColor()));
    }

    /// <summary>
    /// Called when a remote client state changes with the server.
    /// </summary>
    /// <param name="connection"></param>
    /// <param name="args"></param>
    private void ServerManager_OnRemoteConnectionState(NetworkConnection connection, RemoteConnectionStateArgs args)
    {
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on server remote connection state, connection[{connection}] state[{args.ConnectionState}]'".Color(GetDebug().GetColor()));
    }

    /// <summary>
    /// Called when a client loads initial scenes after connecting.
    /// Boolean will be true if asServer.
    /// This will invoke even if the SceneManager is not used when the client completes fully connecting to the server.
    /// </summary>
    /// <param name="connection"></param>
    /// <param name="asServer"></param>
    private void SceneManager_OnClientLoadedStartScenes(NetworkConnection connection, bool asServer)
    {
        if (!asServer) return;
        
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on scene manager client loaded start scenes ClientId[{connection.ClientId}] asServer[{asServer}]".Color(GetDebug().GetColor()));

        FishNetAuthenticator authenticator = GetAuthenticator();

        if (!authenticator.GetAuthenticationData(connection, out FishNetAuthenticator.AuthRequest r))
        {
            if(GetDebug().LogWarning)
                Debug.LogWarning($"Server could found auth data for the given client id '{connection.ClientId}'".Color(GetDebug().GetColor()));
            connection.Disconnect(true);
        }

        SpawnPlayerClient(connection, r.username, r.characterModelPath);
    }


    /// <summary>
    /// Called when a scene load starts.
    /// </summary>
    /// <param name="args"></param>
    private void SceneManager_OnLoadStart(SceneLoadStartEventArgs args)
    {
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on scene manager load start".Color(GetDebug().GetColor()));
        App.Instance.GetGame().ClearCurrentLevel();
        _onSceneManagerLoadStart.Invoke(args);
    }

    /// <summary>
    /// Called when completion percentage changes while loading a scene.
    /// Value is between 0f and 1f, while 1f is 100% done.
    /// Can be used for custom progress bars when loading scenes.
    /// </summary>
    /// <param name="args"></param>
    private void SceneManager_OnLoadPercentChange(SceneLoadPercentEventArgs args)
    {
        LoadQueueData q = args.QueueData;
        
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on scene manager load percent change percent[{args.Percent}] asServer[{q.AsServer}] scopeType[{q.ScopeType}] globalScenes[{string.Join(", ", q.GlobalScenes)}]".Color(GetDebug().GetColor()));
        _onSceneManagerLoadPercentChange.Invoke(args);
    }

    /// <summary>
    /// Called when a scene load ends.
    /// </summary>
    /// <param name="args"></param>
    private void SceneManager_OnLoadEnd(SceneLoadEndEventArgs args)
    {
        bool asServer = args.QueueData.AsServer;

        Scene[] loadedScenes = args.LoadedScenes;
        int loadedScenesCount = loadedScenes?.Length ?? 0;

        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on scene manager load end AsServer[{asServer}] loadedScenesCount[{loadedScenesCount}]".Color(GetDebug().GetColor()));

        if (loadedScenesCount == 0)
        {
            return;
        }

        AppGame game = App.Instance.GetGame();
        Scene loadedFirstScene = loadedScenes[0];
        
        game.GetPlayer().GetCamera().ReturnHome();
        game.UnloadMainMenu();
        game.UpdateCurrentLevel(loadedFirstScene);

        if (asServer && !_agentsInitialized)
        {
            _agentsInitialized = true;

            foreach (AgentEntity agent in game.CreateAgents(game.GetGameData().scene.agents))
            {
                _networkManager.ServerManager.Spawn(agent.GetCharacter().gameObject);
            }

            // We allow clients to join now.
            GetAuthenticator().SetAllowClientAuthentications(true);
            App.Instance.GetUI().HideLobby();
        }
        
        if (asServer)
        {
            _serverLoadSceneProcess.onCompleted.Invoke();
            _serverLoadSceneProcess = null;
        }

        _onSceneManagerLoadEnd.Invoke(args);
    }

    /// <summary>
    /// Called after the local client connection state changes.
    /// </summary>
    /// <param name="obj"></param>
    private void ClientManager_OnClientConnectionState(ClientConnectionStateArgs obj)
    {
        _stateClient = obj.ConnectionState;
        
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on client connection state changed '{_stateClient}'".Color(GetDebug().GetColor()));

        switch (obj.ConnectionState)
        {
            case LocalConnectionState.Started:
                {
                    _isClientConnected = true;
                    _onClientConnectionStarted.Invoke();
                    break;
                }
            case LocalConnectionState.Stopped:
                {
                    bool wasConnected = _isClientConnected;
                    _isClientConnected = false;

                    if (wasConnected)
                    {
                        _onClientDisconnected.Invoke();
                    }
                    else
                    {
                        _onClientConnectionFailed.Invoke();
                    }
                    break;
                }
        }
    }



    /// <summary>
    /// Called after local client has authenticated.
    /// </summary>
    private void ClientManager_OnAuthenticated()
    {
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name} on client authenticated".Color(GetDebug().GetColor()));
    }

    public void SetNetwork(string networkAddress, ushort portStandalone, ushort portWeb)
    {
        _transportTugboat.SetClientAddress(networkAddress);
        _transportTugboat.SetPort(portStandalone);

        _transportBayou.SetClientAddress(networkAddress);
        _transportBayou.SetPort(portWeb);
    }

    /// <summary>
    /// Starts the server if configured to for headless.
    /// </summary>
    [Button]
    public void StartServer()
    {
        if (_stateServer != LocalConnectionState.Stopped)
        {
            if(GetDebug().LogWarning)
                Debug.LogWarning($"{GetType().Name}.StartServer skipped, already {_stateServer}.".Color(GetDebug().GetColor()));
            return;
        }

        Multipass mp = GetMultipass();

        if(GetDebug().LogInfo)
            Debug.Log($"{nameof(AppNetwork)}.StartServer() with transports {string.Join(", ", mp.Transports.Select(i => i.GetType().Name).ToArray())}".Color(GetDebug().GetColor()));

        GetAuthenticator().SetAllowClientAuthentications(false);
        _networkManager.ServerManager.StartConnection();
    }

    /// <summary>
    /// Stops the local server connection.
    /// </summary>
    [Button]
    public void StopServer()
    {
        if (_stateServer == LocalConnectionState.Stopped)
        {
            if(GetDebug().LogWarning)
                Debug.LogWarning($"{GetType().Name}.StopServer skipped, already {_stateServer}.".Color(GetDebug().GetColor()));
            return;
        }
        _networkManager.ServerManager.StopConnection(true);
    }

    /// <summary>
    /// Starts the local client connection.
    /// </summary>
    [Button]
    public void StartClient()
    {
        if (_stateClient != LocalConnectionState.Stopped)
        {
            if(GetDebug().LogWarning)
                Debug.LogWarning($"{GetType().Name}.StartClient skipped, already {_stateClient}.".Color(GetDebug().GetColor()));
            return;
        }

        Multipass mp = GetMultipass();

#if UNITY_WEBGL && !UNITY_EDITOR
        mp.SetClientTransport<Bayou>();
                    if (mp.GetTransport<Bayou>().GetClientAddress() == "localhost")
        {
            Debug.LogWarning("Bayou client address is set to localhost, using ws://.".Color(GetDebug().GetColor()));
            mp.GetTransport<Bayou>().SetClientUseDefaultPort(false);
            mp.GetTransport<Bayou>().SetUseWSS(false);
        } else {
            mp.GetTransport<Bayou>().SetClientUseDefaultPort(true);
            mp.GetTransport<Bayou>().SetUseWSS(true);
        }
#else
        mp.SetClientTransport<Tugboat>();
#endif

        if(GetDebug().LogInfo)
            Debug.Log($"{nameof(AppNetwork)}.StartClient() with client transport {mp.ClientTransport.GetType().Name}".Color(GetDebug().GetColor()));
        _networkManager.ClientManager.StartConnection();
    }

    /// <summary>
    /// Stops the local client connection.
    /// </summary>
    [Button]
    public void StopClient()
    {
        if (_stateClient == LocalConnectionState.Stopped)
        {
            if(GetDebug().LogWarning)
                Debug.LogWarning($"{GetType().Name}.StopClient skipped, already {_stateClient}.".Color(GetDebug().GetColor()));
            return;
        }
        _networkManager.ClientManager.StopConnection();
    }

    private void SpawnPlayerClient(NetworkConnection clientConnection, string username, string characterModelPath)
    {
        if (_playerPrefab == null)
        {
            if(GetDebug().LogWarning)
                Debug.LogWarning($"Player prefab is empty and cannot be spawned".Color(GetDebug().GetColor()));
            return;
        }

        if (!App.Instance.GetGame().GetCurrentLevel(out LyfeCreatorSceneData sceneData))
        {
            if(GetDebug().LogWarning)
                Debug.LogWarning($"No current level is active, aborting player spawn..".Color(GetDebug().GetColor()));
            return;
        }

        NetworkObject nob = _networkManager.GetPooledInstantiated(_playerPrefab, true);
        ClientNetworkBehaviour client = nob.GetComponent<ClientNetworkBehaviour>();

        client.SetSyncId(App.Instance.GetGame().GenerateId());
        client.FromServer_SetUsername(username);
        client.FromServer_SetPermission(CharacterPermission.Player);
        client.FromServer_SetCharacterModelPath(characterModelPath);

        client.SetPositionAndRotation(sceneData.GetRandomSpawnPoint(), 0f);

        // The player is owned by the connection.
        _networkManager.ServerManager.Spawn(nob, clientConnection);
    }

    public void DisconnectAllClients(bool includeServerClient)
    {
        foreach (KeyValuePair<int, NetworkConnection> client in _networkManager.ServerManager.Clients)
        {
            NetworkConnection connection = client.Value;
            if(connection == null || !connection.IsActive) continue;

            // Disconnect everyone
            if (includeServerClient)
            {
                connection.Disconnect(false);
            }
            // Disconnect everyone besides server client
            else
            {
                if(!connection.IsLocalClient) connection.Disconnect(false);
            }
        }
    }
}
