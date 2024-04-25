using Lyfe.Creator.v1;
using UnityEngine;

public class LyfeCreatorDataWorldShape
{
    public LyfeCreatorWorldShapeKind kind;
    public float radiusMin;
    public float radiusMax;
    public Vector3 sizeMin;
    public Vector3 sizeMax;
    public LyfeCreatorDataCollider collider;


    /// <summary>
    /// Constructor.
    /// </summary>
    /// <param name="kind"></param>
    /// <param name="radiusMin"></param>
    /// <param name="radiusMax"></param>
    /// <param name="sizeMin"></param>
    /// <param name="sizeMax"></param>
    /// <param name="collider"></param>
    public LyfeCreatorDataWorldShape(
        LyfeCreatorWorldShapeKind kind,
        float radiusMin,
        float radiusMax,
        Vector3 sizeMin,
        Vector3 sizeMax,
        LyfeCreatorDataCollider collider)
    {
        this.kind = kind;
        this.radiusMin = radiusMin;
        this.radiusMax = radiusMax;
        this.sizeMin = sizeMin;
        this.sizeMax = sizeMax;
        this.collider = collider;
    }


    /// <summary>
    /// Static resolver for v1 world shape.
    /// </summary>
    /// <param name="schema"></param>
    /// <param name="collider"></param>
    /// <param name="result"></param>
    /// <returns></returns>
    public static bool Resolve(LyfeCreator_v1_WorldShape schema, LyfeCreatorDataCollider colliderData, out LyfeCreatorDataWorldShape result)
    {
        result = null;
        if (schema == null) return false;
        
        LyfeCreator_v1_WorldShapeKind v1Kind = schema.kind;
        LyfeCreatorWorldShapeKind kind;
            
        // Resolve kind
        switch (v1Kind)
        {
            case LyfeCreator_v1_WorldShapeKind.Sphere:
            {
                kind = LyfeCreatorWorldShapeKind.Sphere;
                break;
            }
            case LyfeCreator_v1_WorldShapeKind.Rect:
            {
                kind = LyfeCreatorWorldShapeKind.Rect;
                break;
            }
            case LyfeCreator_v1_WorldShapeKind.Circle:
            {
                kind = LyfeCreatorWorldShapeKind.Circle;
                break;
            }
            default:
            {
                Debug.LogWarning($"Unrecognized {nameof(LyfeCreator_v1_WorldShapeKind)}.{v1Kind}");
                return false;
            }
        }

        result = new LyfeCreatorDataWorldShape(
            kind,
            schema.radiusMin,
            schema.radiusMax,
            schema.sizeMin,
            schema.sizeMax,
            colliderData);
        
        return result != null;
    }
}
