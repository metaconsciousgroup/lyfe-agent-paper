using UnityEngine;

[CreateAssetMenu(fileName = "App Config Environment - ", menuName = "SO/App/Config Environment", order = 1)]
public class SOAppConfigEnvironment : SO
{
    [SerializeField] private AppKind _kind;
    [SerializeField] private NetworkData _network;
    [SerializeField] private SOUIViewLobby _lobby;
    [SerializeField] private SOPython _python;
    
    [Header(H_L + "App" + H_R)]
    [SerializeField] private bool _runInBackground;
    [SerializeField] private int _targetFrameRate;

    [Header(H_L + "Server-Only" + H_R)]
    [SerializeField] private bool _forcePythonConnection;

    [Header(H_L + "Debug" + H_R)]
    [SerializeField] private bool _showCharacterInformation;
    [SerializeField] private int _consoleMaxMessages;
    [SerializeField] private SODebug _debugGame;
    [SerializeField] private SODebug _debugNetwork;
    [SerializeField] private SODebug _debugNetworkClient;
    [SerializeField] private SODebug _debugPython;
    [SerializeField] private SODebug _debugAuthentication;

    [SerializeField] private SOLyfeCreatorSettings _creatorSettings;

#if UNITY_EDITOR
    protected override void Reset()
    {
        base.Reset();
        _network = new NetworkData("localhost", 7777, 7778, "Player");
    }
#endif

    public bool runInBackground => _runInBackground;
    public int targetFrameRate => _targetFrameRate;
    public AppKind GetKind() => _kind;
    public NetworkData GetNetwork() => _network;
    public SOUIViewLobby GetLobby() => _lobby;
    public SOPython GetPython() => _python;
    public bool forcePythonConnection => _forcePythonConnection;
    public bool showCharacterInformation => _showCharacterInformation;
    public int consoleMaxMessages => _consoleMaxMessages;
    public SODebug GetDebugGame() => _debugGame;
    public SODebug GetDebugNetwork() => _debugNetwork;
    public SODebug GetDebugNetworkClient() => _debugNetworkClient;
    public SODebug GetDebugPython() => _debugPython;
    public SODebug GetDebugAuthentication() => _debugAuthentication;

    public SOLyfeCreatorSettings GetCreatorSettings() => _creatorSettings;
}
