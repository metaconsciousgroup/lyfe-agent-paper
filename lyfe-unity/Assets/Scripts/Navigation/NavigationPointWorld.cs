using UnityEngine;

public class NavigationPointWorld : NavigationPoint
{
    private LyfeCreatorWorldArea _area;
    private Vector3 _point;
    
    private NavigationPointWorld(LyfeCreatorWorldArea area)
    {
        this._area = area;
        this._point = area.GetPoint();
    }

    public override string GetKey() => _area.GetKey();

    public override Vector3 GetPoint() => _point;

    public override bool IsPointDynamic() => false;
    
    public override float GetStoppingDistance() => 0f;

    public override bool IsValid() => _area != null;

    public override NavigationPointKind GetKind() => NavigationPointKind.World;

    public static NavigationPointWorld From(LyfeCreatorWorldArea value) => new (value);
}
