using UnityEngine;


public abstract class NavigationPoint
{
    
    public abstract string GetKey();
    public abstract Vector3 GetPoint();
    public abstract bool IsPointDynamic();
    
    public abstract float GetStoppingDistance();

    public abstract bool IsValid();

    public abstract NavigationPointKind GetKind();
}