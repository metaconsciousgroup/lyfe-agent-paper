using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

public class AppEntities : BaseMonoBehaviour
{
    [SerializeField] private AppEntitiesCharacters _characters;
    [SerializeField] private AppEntitiesItems _items;
    private readonly int _scanLevel = 2;

    public AppEntitiesCharacters GetCharacters() => _characters;
    public AppEntitiesItems GetItems() => _items;
    
    [Button]
    public List<NetworkEntity> GetAll() => transform.GetComponentsPro<NetworkEntity>(GetComponentProExtensions.Scan.Down, 1, _scanLevel);
    
    public bool GetById(string id, out NetworkEntity networkEntity)
    {
        networkEntity = null;
        if (string.IsNullOrEmpty(id)) return false;
        
        foreach (NetworkEntity i in transform.GetComponentsPro<NetworkEntity>(GetComponentProExtensions.Scan.Down, 1, _scanLevel)) {
            if (i.GetSyncId() == id)
            {
                networkEntity = i;
                break;
            }
        }
        return networkEntity != null;
    }
}
