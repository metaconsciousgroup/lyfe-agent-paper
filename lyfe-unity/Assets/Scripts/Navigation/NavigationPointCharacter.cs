using UnityEngine;

public class NavigationPointCharacter : NavigationPoint
{
    private CharacterEntity _character;
    private float _stoppingDistance;

    private NavigationPointCharacter(CharacterEntity value)
    {
        _character = value;
        _stoppingDistance = Random.Range(0.6f, 2f);
    }

    public override string GetKey() => _character.GetUser().Id.GetValue();
    public override Vector3 GetPoint() => _character.transform.position;

    public override bool IsPointDynamic() => true;
    
    public override float GetStoppingDistance() => _stoppingDistance;

    public override bool IsValid() => _character != null;

    public override NavigationPointKind GetKind() => NavigationPointKind.Character;
    
    
    public static NavigationPointCharacter From(CharacterEntity value) => new (value);
}
