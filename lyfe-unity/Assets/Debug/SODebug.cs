using UnityEngine;

[CreateAssetMenu(fileName = "Debug - ", menuName = "SO/App/Debug/Option", order = 1)]
public class SODebug : SO
{
    [SerializeField] private bool _logInfo;
    [SerializeField] private bool _logWarning;
    [SerializeField] private bool _logError;
    [SerializeField] private SOValueColor _color;

    public bool LogInfo => _logInfo;
    public bool LogWarning => _logWarning;
    public bool LogError => _logError;

    public Color GetColor() => _color.GetValue();
}
