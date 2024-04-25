using System.Collections.Generic;
using System.Linq;
using Sirenix.OdinInspector;
using UnityEngine;

public class NearByCharacters : NearBy<CharacterEntity>
{
    [ReadOnly, ShowInInspector] private Dictionary<CharacterPermission, HashSet<CharacterEntity>> _charactersMappedByPermission = new();
    
#if UNITY_EDITOR
    /// <summary>
    /// Draws NearByCharacters gizmos.
    /// </summary>
    /// <param name="source"></param>
    /// <param name="type"></param>
    [UnityEditor.DrawGizmo(UnityEditor.GizmoType.NotInSelectionHierarchy | UnityEditor.GizmoType.Selected | UnityEditor.GizmoType.InSelectionHierarchy)]
    private static void DrawGizmo(NearByCharacters source, UnityEditor.GizmoType type)
    {
        Transform tr = source.transform;
        Vector3 pivot = tr.position + (tr.up * 1f);
        foreach (CharacterEntity entity in source.GetAll())
        {
            UnityEditor.Handles.DrawLine(pivot, entity.transform.position);
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

    protected override void OnEntered(CharacterEntity target)
    {
        CharacterPermission permission = target.GetPermission();
        HashSet<CharacterEntity> set;
        if (_charactersMappedByPermission.ContainsKey(permission))
        {
            set = _charactersMappedByPermission[permission];
        }
        else
        {
            set = new HashSet<CharacterEntity>();
            _charactersMappedByPermission.Add(permission, set);
        }
        set.Add(target);
    }

    protected override void OnExited(CharacterEntity target)
    {
        CharacterPermission permission = target.GetPermission();
        if (_charactersMappedByPermission.ContainsKey(permission))
        {
            _charactersMappedByPermission[permission].Remove(target);
        }
    }

    public HashSet<CharacterEntity> GetAllWithPermission(CharacterPermission permission)
    {
        if (!_charactersMappedByPermission.ContainsKey(permission))
            return new HashSet<CharacterEntity>(0);
        return _charactersMappedByPermission[permission];
    }
    
        
    public bool GetClosest(out CharacterEntity target, CharacterPermission permission)
    {
        target = null;
        List<CharacterEntity> all = GetAll().ToList();
        Vector3 currentPos = transform.position;
        target = all
            .Where(i => i.GetPermission() == permission)
            .OrderBy(i => Vector3.Distance(currentPos, i.transform.position)).FirstOrDefault();
        return target != null;
    }

}
