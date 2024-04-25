using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

public class VisibleCharacters : NearBy<CharacterEntity>
{
    [ReadOnly, ShowInInspector] private Dictionary<CharacterPermission, HashSet<CharacterEntity>> _visibleCandidates = new();
    [SerializeField]
    private LayerMask ignoreLayerMask;
    [SerializeField] private float characterHeight = 0.75f;
    [SerializeField] private float fieldOfView = 120f;
    [SerializeField] private CharacterEntity _characterEntity;
    private RaycastHit[] raycastHits = new RaycastHit[1];

#if UNITY_EDITOR
    [UnityEditor.DrawGizmo(UnityEditor.GizmoType.NotInSelectionHierarchy | UnityEditor.GizmoType.Selected | UnityEditor.GizmoType.InSelectionHierarchy)]
    private static void DrawGizmo(VisibleCharacters source, UnityEditor.GizmoType type)
    {
        Transform tr = source.transform;
        Vector3 pivot = tr.position + (Vector3.up * source.characterHeight);
        UnityEditor.Handles.color = Color.red;
        foreach (CharacterEntity entity in source.GetAll())
        {
            UnityEditor.Handles.DrawLine(pivot, entity.transform.position + (Vector3.up * source.characterHeight));
        }
    }
#endif

    protected override bool OnEnterCheck(GameObject other, out CharacterEntity target)
    {
        target = other.GetComponent<CharacterEntity>();
        return target != null;
    }

    protected override bool OnExitCheck(GameObject other, out CharacterEntity target)
    {
        target = other.GetComponent<CharacterEntity>();
        return target != null;
    }

    private bool IsVisible(CharacterEntity target)
    {
        Vector3 origin = transform.position + (Vector3.up * characterHeight);
        Vector3 targetPosition = target.transform.position + (Vector3.up * characterHeight);
        Vector3 directionToTarget = targetPosition - origin;
        directionToTarget.y = 0; // For FOV calculation, we consider only the horizontal plane

        // Check if target is within field of view
        if (Vector3.Angle(_characterEntity.GetRotation().forward, directionToTarget.normalized) > fieldOfView / 2)
        {
            return false;
        }

        float distanceToTarget = directionToTarget.magnitude;
        int hitCount = Physics.RaycastNonAlloc(origin, directionToTarget.normalized, raycastHits, distanceToTarget, ~ignoreLayerMask);
        if (hitCount > 0)
        {
            RaycastHit hit = raycastHits[0];
            if (hit.collider.gameObject == target.gameObject)
            {
                return true;
            }
            return false;
        }
        return true;
    }

    protected override void OnEntered(CharacterEntity target)
    {
        CharacterPermission permission = target.GetPermission();
        HashSet<CharacterEntity> set;
        if (_visibleCandidates.ContainsKey(permission))
        {
            set = _visibleCandidates[permission];
        }
        else
        {
            set = new HashSet<CharacterEntity>();
            _visibleCandidates.Add(permission, set);
        }
        set.Add(target);
    }

    protected override void OnExited(CharacterEntity target)
    {
        CharacterPermission permission = target.GetPermission();
        if (_visibleCandidates.ContainsKey(permission))
        {
            _visibleCandidates[permission].Remove(target);
        }
    }

    [Button]
    public HashSet<CharacterEntity> GetAllWithPermission(CharacterPermission permission)
    {
        if (!_visibleCandidates.ContainsKey(permission))
            return new HashSet<CharacterEntity>(0);
        HashSet<CharacterEntity> candidates = _visibleCandidates[permission];
        HashSet<CharacterEntity> visible = new HashSet<CharacterEntity>();
        foreach (CharacterEntity candidate in candidates)
        {
            if (IsVisible(candidate))
            {
                visible.Add(candidate);
            }
        }
        return visible;
    }
}
