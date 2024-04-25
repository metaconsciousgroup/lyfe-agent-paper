using UnityEngine;

[System.Serializable]
public class TransformData
{
    public Vector3Data position;
    public Vector3Data rotation;

    public TransformData() { }
    
    public TransformData(Vector3Data position, Vector3Data rotation)
    {
        this.position = position;
        this.rotation = rotation;
    }

    public static TransformData From(Transform transform)
    {
        return new TransformData(
            Vector3Data.FromVector3(transform.position),
            Vector3Data.FromVector3(transform.eulerAngles));
    }
}
