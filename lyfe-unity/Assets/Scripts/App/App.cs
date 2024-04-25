using Sirenix.OdinInspector;
using UnityEngine;

public class App : Singleton<App>
{
    [SerializeField] private AppUI _uI;
    [SerializeField] private ReadyPlayerMeManager _readyPlayerMeManager;
    [SerializeField] private AppGame _game;
    [SerializeField] private AppAudio _audio;
    [SerializeField] private AppPythonWebSocket _pythonWebSocket;
    [SerializeField] private SceneLoader _sceneLoader;
    [SerializeField] private SOAppConfig _config;


    public AppUI GetUI() => _uI;
    public AppAudio GetAudio() => _audio;
    public ReadyPlayerMeManager GetReadyPlayerMeManager() => _readyPlayerMeManager;
    public AppGame GetGame() => _game;
    public AppPythonWebSocket GetPythonWebSocket() => _pythonWebSocket;
    public SOAppConfig GetConfig() => _config;
    public SceneLoader GetSceneLoader() => _sceneLoader;


    protected override void Awake()
    {
        base.Awake();
        Debug.Log($"Launching app with config '{_config.GetEnvironment().GetKind()}'");
        DontDestroyOnLoad(gameObject);
    }

    protected override void Start()
    {
        base.Start();
        GetGame().LoadMainMenu();
    }


    [Button]
    public void Quit()
    {
#if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
#elif UNITY_WEBGL
        // closeBrowserWindow();
#else
        Application.Quit();
#endif
    }
}
