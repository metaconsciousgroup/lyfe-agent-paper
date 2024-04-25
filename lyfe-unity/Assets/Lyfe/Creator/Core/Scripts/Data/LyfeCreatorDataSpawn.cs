
using Lyfe.Creator.v1;
using UnityEngine;

public class LyfeCreatorDataSpawn
{
    /// <summary>
    /// Shape data.
    /// Null is allowed if shape doesnt exist.
    /// </summary>
    public LyfeCreatorDataWorldShape shape;
    public Transform targetTransform;
    
    private static LyfeCreatorDataCollider ColliderData = new (LyfeCreatorColliderKind.None);
    
    
    public LyfeCreatorDataSpawn(Transform targetTransform, LyfeCreatorDataWorldShape shape)
    {
        this.targetTransform = targetTransform;
        this.shape = shape;
    }
    
    
    /// <summary>
    /// Static resolver for v1 world area.
    /// </summary>
    /// <param name="schema"></param>
    /// <returns></returns>
    public static LyfeCreatorDataSpawn Resolve(LyfeCreator_v1_Spawn schema)
    {
        LyfeCreatorDataWorldShape.Resolve(schema.shape, ColliderData, out LyfeCreatorDataWorldShape shape);
        return new (schema.transform, shape);
    }
}
