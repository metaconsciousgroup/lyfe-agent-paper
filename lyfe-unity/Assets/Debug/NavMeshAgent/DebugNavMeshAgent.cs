using UnityEngine;
using UnityEngine.AI;

/// <summary>
/// Debugs NavMeshAgent with gizmos and handles.
/// </summary>
public class DebugNavMeshAgent : BaseMonoBehaviour
{
    [Tooltip("Target NavMeshAgent behaviour.")]
    [SerializeField] private NavMeshAgent _navMeshAgent;
    [Tooltip("Gizmos & Handles render settings.")]
    [SerializeField] private SODebugNavMeshAgentSettings _settings;
    
#if UNITY_EDITOR
    /// <summary>
    /// Draws NavMeshAgent gizmos.
    /// </summary>
    /// <param name="source"></param>
    /// <param name="type"></param>
    [UnityEditor.DrawGizmo(UnityEditor.GizmoType.NotInSelectionHierarchy | UnityEditor.GizmoType.Selected | UnityEditor.GizmoType.InSelectionHierarchy)]
    private static void DrawGizmo(DebugNavMeshAgent source, UnityEditor.GizmoType type)
    {
        NavMeshAgent agent = source._navMeshAgent;
        SODebugNavMeshAgentSettings settings = source._settings;
        
        if (agent == null) return;
        if (!agent.enabled) return;

        DrawPath(agent.path, settings);
        
        // Draws NavMeshAgent active path.
        static void DrawPath(NavMeshPath path, SODebugNavMeshAgentSettings settings)
        {
            if (path == null) return;
            Vector3[] corners = path.corners;
            if (corners == null) return;

            if (settings != null)
            {
                UnityEditor.Handles.color = settings.GetColorPathLine();
            }
            
            int max = corners.Length - 1;
            for (int i = 0; i < max; i++)
            {
                Vector3 a = corners[i];
                Vector3 b = corners[i + 1];
                
                UnityEditor.Handles.DrawLine(a, b);
            }
        }
    }
#endif
}
