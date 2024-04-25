using System;
using System.Collections.Generic;
using System.Linq;
using Sirenix.OdinInspector;
using UnityEngine;

public class TransformVelocity : BaseMonoBehaviour
{
    [Tooltip("Debug draw gizmos speed.")]
    [SerializeField] private bool _drawGizmosSpeed;
    [Tooltip("Debug draw gizmos speed smoothed.")]
    [SerializeField] private bool _drawGizmosSpeedSmooth;
    [Tooltip("Maximum clamped speed value, ignored if value is negative.")]
    [SerializeField] private float _speedMax;
    [Tooltip("Speed of how fast speed smooth will catch up to target speed value. If negative then updated instantly.")]
    [SerializeField] private float _speedSmoothSpeed;
    [Tooltip("Update kind when values are recalculated.")]
    [SerializeField] private UnityUpdateKind _updateKind;
    [SerializeField] private int _speedWindow = 100;
    [ShowInInspector, ReadOnly]
    private Queue<float> _speedWindowQueue = new Queue<float>();

    private float _speed;
    private float _speedSmooth;
    private Vector3 _previousPosition;
    private const string GizmosSpeedFormat = "F2";

    private enum UnityUpdateKind
    {
        Update,
        LateUpdate
    }

    public float GetSpeed() => _speed;

    public float GetSpeedSmooth() => _speedSmooth;

#if UNITY_EDITOR
    protected override void Reset()
    {
        base.Reset();
        _updateKind = UnityUpdateKind.LateUpdate;
        _speedMax = -1f;
        _speedSmoothSpeed = -1f;
    }

    [UnityEditor.DrawGizmo(UnityEditor.GizmoType.NotInSelectionHierarchy | UnityEditor.GizmoType.Selected | UnityEditor.GizmoType.InSelectionHierarchy)]
    private static void DrawGizmo(TransformVelocity source, UnityEditor.GizmoType type)
    {
        UnityEditor.Handles.Label(source.transform.position, $"cur:{source.GetSpeed().ToString(GizmosSpeedFormat)} smo:{source.GetSpeedSmooth().ToString(GizmosSpeedFormat)}");
    }
#endif

    protected override void OnEnable()
    {
        base.OnEnable();
        Clear();
    }

    protected override void Start()
    {
        base.Start();
        Clear();
    }

    private void UpdateDelta()
    {
        Vector3 pos = transform.position;
        Vector3 direction = pos - _previousPosition;
        _speed = direction.magnitude / Time.deltaTime;
        
        _speedWindowQueue.Enqueue(_speed);
        if (_speedWindowQueue.Count >= _speedWindow)
        {
            _speedWindowQueue.Dequeue();
        }
        
        if (_speedMax >= 0f) _speed = Mathf.Clamp(_speed, 0f, _speedMax);
        _speedSmooth = Mathf.Lerp(_speedSmooth, _speed, Time.deltaTime * _speedSmoothSpeed);

        _previousPosition = pos;
    }

    private void Clear()
    {
        _speed = 0f;
        _speedSmooth = 0f;
        _previousPosition = transform.position;
    }

    private void Update()
    {
        switch (_updateKind)
        {
            case UnityUpdateKind.Update:
                {
                    UpdateDelta();
                    break;
                }
        }
    }

    private void LateUpdate()
    {
        switch (_updateKind)
        {
            case UnityUpdateKind.LateUpdate:
                {
                    UpdateDelta();
                    break;
                }
        }
    }
}
