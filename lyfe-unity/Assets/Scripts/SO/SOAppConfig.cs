using UnityEngine;

[CreateAssetMenu(fileName = "App Config", menuName = "SO/App/Config", order = 1)]
public class SOAppConfig : SO
{
    [SerializeField] private SOAppConfigEnvironment _environment;
    [SerializeField] private SOResourcesSOEmote _emotes;
    [SerializeField] private SOResourcesSOItem _items;
    [SerializeField] private SOPrefabs _prefabs;
    [SerializeField] private SOReadyPlayerMe _readyPlayerMe;
    
    [SerializeField] private SOLeaveForLocation _leaveForLocation;

    public SOAppConfigEnvironment GetEnvironment() => _environment;

    public SOLeaveForLocation GetLeaveForLocation() => _leaveForLocation;
    public SOResourcesSOEmote GetEmotes() => _emotes;
    public SOPrefabs GetPrefabs() => _prefabs;
    public SOResourcesSOItem GetItems() => _items;
    public SOReadyPlayerMe GetReadyPlayerMe() => _readyPlayerMe;

    // Adding a public function to allow scripts to update the _current field.
    public void SetEnvironment(SOAppConfigEnvironment environment) => _environment = environment;
}
