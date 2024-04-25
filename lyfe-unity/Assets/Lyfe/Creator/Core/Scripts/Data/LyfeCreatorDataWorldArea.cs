using Lyfe.Creator.v1;
using UnityEngine;

public class LyfeCreatorDataWorldArea
{
    public string key;
    /// <summary>
    /// Shape data.
    /// Null is allowed if shape doesnt exist.
    /// </summary>
    public LyfeCreatorDataWorldShape shape;

    public Transform targetTransform;

    private static LyfeCreatorDataCollider ColliderData = new (LyfeCreatorColliderKind.Trigger);

    public LyfeCreatorDataWorldArea(string key, Transform targetTransform, LyfeCreatorDataWorldShape shape)
    {
        this.key = key;
        this.targetTransform = targetTransform;
        this.shape = shape;
    }

    /// <summary>
    /// Static resolver for v1 world area.
    /// </summary>
    /// <param name="schema"></param>
    /// <returns></returns>
    public static LyfeCreatorDataWorldArea Resolve(LyfeCreator_v1_WorldArea schema)
    {
        LyfeCreatorDataWorldShape.Resolve(schema.shape, ColliderData, out LyfeCreatorDataWorldShape shape);
        return new (schema.key, schema.transform, shape);
    }
}
