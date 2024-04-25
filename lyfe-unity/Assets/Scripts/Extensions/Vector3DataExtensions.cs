using UnityEngine;

public static class Vector3DataExtensions
{
    
    public static Vector3 GetVector3(this Vector3Data value)
    {
        if (value == null) return Vector3.zero;
        return new Vector3(value.x, value.y, value.z);
    }
}
