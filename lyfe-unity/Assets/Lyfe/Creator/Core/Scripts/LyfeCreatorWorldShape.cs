using Sirenix.OdinInspector;
using UnityEngine;

public class LyfeCreatorWorldShape : MonoBehaviour
{
    [ReadOnly, ShowInInspector] private LyfeCreatorWorldShapeKind _kind;
    [ReadOnly, ShowInInspector] private float _radiusMin;
    [ReadOnly, ShowInInspector] private float _radiusMax;
    [ReadOnly, ShowInInspector] private Vector3 _sizeMin;
    [ReadOnly, ShowInInspector] private Vector3 _sizeMax;
    [Space]
    private Collider _collider;


    public void SetData(LyfeCreatorDataWorldShape shapeData)
    {
        if (shapeData == null)
        {
            Clear();
            return;
        }
        _kind = shapeData.kind;
        _radiusMin = shapeData.radiusMin;
        _radiusMax = shapeData.radiusMax;
        _sizeMin = shapeData.sizeMin;
        _sizeMax = shapeData.sizeMax;
        
        ClearCollider();
        
        // Now update collider options
        LyfeCreatorDataCollider colliderData = shapeData.collider;

        // No collider needed whatsoever
        if (colliderData.kind == LyfeCreatorColliderKind.None)
        {
            return;
        }

        switch (_kind)
        {
            case LyfeCreatorWorldShapeKind.Circle:
            case LyfeCreatorWorldShapeKind.Sphere:
            {
                SphereCollider sphereCollider = gameObject.AddComponent<SphereCollider>();
                sphereCollider.radius = _radiusMax;
                _collider = sphereCollider;
                break;
            }
            case LyfeCreatorWorldShapeKind.Rect:
            {
                BoxCollider boxCollider = gameObject.AddComponent<BoxCollider>();
                boxCollider.size = _sizeMax;
                _collider = boxCollider;
                break;
            }
            default:
            {
                Debug.LogWarning($"Unrecognized collider {nameof(LyfeCreatorWorldShapeKind)}.{_kind}");
                break;
            }
        }

        // Apply collider settings
        if (_collider != null)
        {
            _collider.isTrigger = colliderData.kind == LyfeCreatorColliderKind.Trigger;
        }
    }

    private void Clear()
    {
        _kind = LyfeCreatorWorldShapeKind.Undefined;
        _radiusMin = 0f;
        _radiusMax = 0f;
        _sizeMin = Vector3.zero;
        _sizeMax = Vector3.zero;
        ClearCollider();
    }

    private void ClearCollider()
    {
        if (_collider == null) return;
        Destroy(_collider);
        _collider = null;
    }
    
    public Vector3 GetPoint()
    {
        switch (_kind)
        {
            case LyfeCreatorWorldShapeKind.Circle: return GetPointFromCircle();
            case LyfeCreatorWorldShapeKind.Rect: return GetPointFromRect();
            case LyfeCreatorWorldShapeKind.Sphere: return GetPointFromSphere();
        }
        return transform.position;
    }

    private Vector3 GetPointFromCircle()
    {
        float radius = GetRadiusInRange();
        Vector2 r = Random.insideUnitCircle.normalized * radius;

        Transform tr = transform;
        Vector3 point = tr.position;
        point += tr.forward * r.y;
        point += tr.right * r.x;

        return point;
    }

    private Vector3 GetPointFromRect()
    {
        float x = Random.Range(_sizeMin.x * 0.5f, _sizeMax.x * 0.5f);
        float y = Random.Range(_sizeMin.y * 0.5f, _sizeMax.y * 0.5f);
        float z = Random.Range(_sizeMin.z * 0.5f, _sizeMax.z * 0.5f);
        
        float gap = 0.5f;
        if (Random.value > gap) x *= -1f;
        if (Random.value > gap) y *= -1f;
        if (Random.value > gap) z *= -1f;

        Vector3 point = transform.position;
        point += transform.forward * z;
        point += transform.up * y;
        point += transform.right * x;
        
        return point;
    }

    private Vector3 GetPointFromSphere()
    {
       return transform.position + Random.onUnitSphere.normalized * Random.Range(_radiusMin, _radiusMax);
    }

    private float GetRadiusInRange()
    {
        if (Mathf.Abs(_radiusMin - _radiusMax) == 0f) return _radiusMin;
        return Random.Range(_radiusMin, _radiusMax);
    }
    
}
