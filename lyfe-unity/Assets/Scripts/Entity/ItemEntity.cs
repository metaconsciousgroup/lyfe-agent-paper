using Sirenix.OdinInspector;
using UnityEngine;

public class ItemEntity : NetworkEntity
{
    [Title("Item")]
    [SerializeField] private SOItem _sO;

    public SOItem GetSO() => _sO;
    
    public override Transform GetExpectedHierarchyParent() => App.Instance.GetGame().GetEntities().GetItems().transform;

    public override bool GetGizmoDebuggerInfo(out string text)
    {
        text = string.Empty;
        if (!GetConfig().GetEnvironment().showCharacterInformation) return false;
        
        text = $"[{GetSyncId()}]";
        return true;
    }

    protected override void OnSyncIdChanged(string prev, string next, bool asServer)
    {
        
    }

    public override bool GetLookAtDestinationPoint(out Vector3 point)
    {
        point = transform.position;
        return true;
    }

}
