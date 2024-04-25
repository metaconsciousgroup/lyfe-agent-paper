using Sirenix.OdinInspector;
using UnityEngine;

public class AppSettings : BaseMonoBehaviour
{
    [SerializeField] private SOAppConfig _config;
    
    
#if UNITY_EDITOR
    protected override void OnValidate()
    {
        base.OnValidate();
        ApplySettings();
    }
#endif
    
    protected override void Awake()
    {
        base.Awake();
        ApplySettings();
    }

    protected override void OnApplicationQuit()
    {
        base.OnApplicationQuit();
    }

    [Button]
    private void ApplySettings()
    {
        if (!IsPlaying()) return;

        SOAppConfigEnvironment current = _config.GetEnvironment();
        Application.runInBackground = current.runInBackground;
        Application.targetFrameRate = current.targetFrameRate;
    }
}
