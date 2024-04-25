using Newtonsoft.Json;
using UnityEngine;

[CreateAssetMenu(fileName = "Python - ", menuName = "SO/App/Config Python", order = 1)]
public class SOPython : SO
{
    [SerializeField] private bool _forceFallback;
    [SerializeField] private float _initWaitTime;
    [SerializeField] private TextAsset _fallbackData;

    public bool ForceFallback() => _forceFallback;
    public float GetInitWaitTime() => _initWaitTime;

    public bool GetFallbackData(out PythonSendInGame data)
    {
        data = null;
        if (_fallbackData != null) data = JsonConvert.DeserializeObject<PythonSendInGame>(_fallbackData.text);
        return data != null;
    }
}
