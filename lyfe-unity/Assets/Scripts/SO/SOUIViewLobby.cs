using UnityEngine;

[CreateAssetMenu(fileName = "UI View - Lobby", menuName = "SO/App/UI/Lobby", order = 1)]
public class SOUIViewLobby : SO
{
    [SerializeField] private bool _showHostName;
    [SerializeField] private bool _showPortStandalone;
    [SerializeField] private bool _showPortWeb;
    [SerializeField] private int _maximumAppearances;
    
    public bool showHostName => _showHostName;
    public bool showPortStandalone => _showPortStandalone;
    public bool showPortWeb => _showPortWeb;
    public int maximumAppearances => _maximumAppearances;
}
