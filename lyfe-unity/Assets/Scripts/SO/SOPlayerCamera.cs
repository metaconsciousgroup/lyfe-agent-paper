using UnityEngine;

[CreateAssetMenu(fileName = "Player Camera", menuName = "SO/App/Player Camera", order = 1)]
public class SOPlayerCamera : SO
{
    [SerializeField] private float _zoomOut;
    [SerializeField] private float _zoomIn;
    [SerializeField] private float _zoomTargetFollowSpeed;
    [Space]
    [SerializeField] private float _targetFollowSpeedMove;
    [SerializeField] private float _targetFollowSpeedRotate;
    [Space]
    [SerializeField] private float _lookSpeedMultiplier;
    [Space]
    [SerializeField] private Vector3 _firstPersonViewCameraOffset;

#if UNITY_EDITOR
    protected override void Reset()
    {
        base.Reset();
        _zoomOut = -8;
        _zoomIn = -2;
        _zoomTargetFollowSpeed = 10f;

        _targetFollowSpeedMove = 7;
        _targetFollowSpeedRotate = 10;

        _lookSpeedMultiplier = 500;
        _firstPersonViewCameraOffset = new Vector3(0, 0.25f, 1.75f);
    }
#endif

    public float GetZoomOut() => _zoomOut;
    public float GetZoomIn() => _zoomIn;
    public float GetZoomTargetFollowSpeed() => _zoomTargetFollowSpeed;
    public float GetTargetFollowSpeedMove() => _targetFollowSpeedMove;
    public float GetTargetFollowSpeedRotate() => _targetFollowSpeedRotate;
    public float GetLookSpeedMultiplier() => _lookSpeedMultiplier;
    public Vector3 GetCameraOverShoulderOffset() => _firstPersonViewCameraOffset;
}
