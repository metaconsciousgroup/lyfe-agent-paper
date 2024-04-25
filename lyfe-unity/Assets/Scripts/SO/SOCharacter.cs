using UnityEngine;

[CreateAssetMenu(fileName = "Character Settings", menuName = "SO/App/Character", order = 1)]
public class SOCharacter : SO
{
    [SerializeField] private float _walk;
    [SerializeField] private float _sprint;
    [SerializeField] private float _rotationCatchUpSpeed;
    [SerializeField] private float _velocityIncreaseSpeed;
    [SerializeField] private float _velocityDecreaseSpeed;

    public float GetWalk() => _walk;
    public float GetSprint() => _sprint;
    public float GetRotationCatchUpSpeed() => _rotationCatchUpSpeed;
    public float GetVelocityIncreaseSpeed() => _velocityIncreaseSpeed;
    public float GetVelocityDecreaseSpeed() => _velocityDecreaseSpeed;

    public float GetSpeedByMoveState(MoveState value)
    {
        switch (value)
        {
            case MoveState.Walking: return _walk;
            case MoveState.Sprinting: return _sprint;
        }
        return 0f;
    }

#if UNITY_EDITOR
    protected override void Reset()
    {
        _walk = 2.5f;
        _sprint = 7.5f;
    }
#endif
}
