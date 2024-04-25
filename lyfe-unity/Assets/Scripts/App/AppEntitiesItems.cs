using System.Collections.Generic;
using Sirenix.OdinInspector;

public class AppEntitiesItems : BaseMonoBehaviour
{
    
    [Button]
    public List<ItemEntity> GetAll() => transform.GetComponentsPro<ItemEntity>(GetComponentProExtensions.Scan.Down, 1, 0);
    
    public bool GetById(string id, out ItemEntity itemEntity)
    {
        itemEntity = null;
        if (string.IsNullOrEmpty(id)) return false;
        
        foreach (ItemEntity i in transform.GetComponentsPro<ItemEntity>(GetComponentProExtensions.Scan.Down, 1, 0))
        {
            if (i.GetSyncId() == id)
            {
                itemEntity = i;
                break;
            }
        }
        return itemEntity != null;
    }

}
