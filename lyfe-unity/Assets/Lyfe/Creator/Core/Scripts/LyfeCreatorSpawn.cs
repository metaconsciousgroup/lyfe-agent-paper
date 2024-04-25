using Sirenix.OdinInspector;
using UnityEngine;

public class LyfeCreatorSpawn : MonoBehaviour
{
    [ReadOnly, ShowInInspector] private LyfeCreatorWorldShape _shape;

    public Vector3 GetPoint() => _shape == null ? transform.position : _shape.GetPoint();
    
    
    public void SetData(LyfeCreatorDataSpawn data)
    {
        if (data.shape == null)
        {
            ClearShape();
            return;
        }

        // Create shape if not already
        if (_shape == null)
        {
            _shape = gameObject.AddComponent<LyfeCreatorWorldShape>();
        }
        
        _shape.SetData(data.shape);
        
        Transform target = data.targetTransform;
        transform.position = target.position;
        transform.rotation = target.rotation;
    }

    private void ClearShape()
    {
        if (_shape == null) return;
        Destroy(_shape);
        _shape = null;
    }
}
