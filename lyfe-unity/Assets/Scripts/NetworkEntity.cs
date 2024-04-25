using FishNet.Object;
using FishNet.Object.Synchronizing;
using FishNet.Transporting;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;

public abstract class NetworkEntity : NetworkBehaviour, ICharacterLookDestination
{
    [Title("Entity")]
    [SerializeField] private SOAppConfig _config;
    [SyncVar(Channel = Channel.Reliable, ReadPermissions = ReadPermission.Observers, OnChange = nameof(OnSyncIdChanged))]
    [SerializeField, ReadOnly] private string _id;
    
    public readonly UnityEvent<ClientNetworkBehaviour> onStartServer = new();
    public readonly UnityEvent<ClientNetworkBehaviour> onStartClient = new();

    public SOAppConfig GetConfig() => _config;
    public string GetSyncId() => _id;

    
    public abstract bool GetGizmoDebuggerInfo(out string text);

    protected virtual void Awake()
    {
        UpdateHierarchyLocation();
    }

    protected virtual void Start()
    {
        UpdateHierarchyLocation();
    }
    
    public override void OnStartNetwork()
    {
        base.OnStartNetwork();
        UpdateHierarchyLocation();
    }
    
    public void SetSyncId(string value)
    {
        string prev = _id;
        _id = value;
        OnSyncIdChanged(prev, value, true);
    }

    protected abstract void OnSyncIdChanged(string prev, string next, bool asServer);

    public abstract bool GetLookAtDestinationPoint(out Vector3 point);

    public abstract Transform GetExpectedHierarchyParent();
    
    private void UpdateHierarchyLocation() => transform.SetParent(GetExpectedHierarchyParent(), false);
}
