using UnityEngine;

[CreateAssetMenu(fileName = "Debug NavMeshAgent", menuName = "SO/App/Debug/NavMeshAgent", order = 1)]
public class SODebugNavMeshAgentSettings : SO
{
    [Tooltip("NavMeshAgent path line color.")]
    [SerializeField] private Color _colorPathLine;
    
    
#if UNITY_EDITOR
    protected override void Reset()
    {
        base.Reset();
        _colorPathLine = Color.yellow;
    }
#endif

    /// <summary>
    /// NavMeshAgent path line color.
    /// </summary>
    /// <returns></returns>
    public Color GetColorPathLine() => _colorPathLine;
}
