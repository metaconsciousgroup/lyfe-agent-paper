using UnityEngine;

[CreateAssetMenu(fileName = "App Settings", menuName = "SO/App/Settings", order = 1)]
public class SOAppSettings : SO
{
    [SerializeField] private SOAppConfig _environment;
    [SerializeField] private SOPlayerCamera _playerCamera;
    [SerializeField] private SOValueColor _minimapColorPlayer;
    [SerializeField] private SOValueColor _minimapColorAgent;


    public SOAppConfig GetEnvironment() => _environment;
    public SOPlayerCamera GetPlayerCamera() => _playerCamera;
    public SOValueColor GetMinimapColorPlayer() => _minimapColorPlayer;
    public SOValueColor GetMinimapColorAgent() => _minimapColorAgent;

    public SOValueColor GetMinimapColor(CharacterPermission characterPermission)
    {
        switch (characterPermission)
        {
            case CharacterPermission.Player: return _minimapColorPlayer;
            case CharacterPermission.Agent: return _minimapColorAgent;
        }
        return null;
    }
}
