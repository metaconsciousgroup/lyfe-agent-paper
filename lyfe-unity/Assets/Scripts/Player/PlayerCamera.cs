using Sirenix.OdinInspector;
using UnityEngine;

namespace Lyfe
{
    public class PlayerCamera : BaseMonoBehaviour
    {
        [SerializeField] private SOPlayerCamera _sO;
        [SerializeField] private CharacterEntity _target;
        [Space]
        [SerializeField] private Camera _mainCamera;
        [SerializeField] private Transform horizontalTransform;
        [SerializeField] private Transform verticalTransform;
        [SerializeField] private Transform _cameraPivot;
        [Space]
        [ReadOnly, ShowInInspector] private float _targetZoom;

        private Vector2 _rotationCurrent;
        private Vector2 _rotationTarget;

        public Camera GetMainCamera() => _mainCamera;
        public Transform GetRotationHorizontal() => horizontalTransform;
        public float GetCurrentZoom() => _cameraPivot.localPosition.z;

        private bool _cameraOverShoulder => App.Instance.GetGame().GetPlayer().IsCameraOverShoulder();

        protected override void Awake()
        {
            base.Awake();
            _targetZoom = _cameraPivot.localPosition.z;
        }

        public void Clear()
        {
            _rotationCurrent = _rotationTarget = Vector2.zero;
            UpdateRotations();
        }

        private void LateUpdate()
        {
            float r = Time.deltaTime * _sO.GetTargetFollowSpeedRotate();

            _rotationCurrent.y = Mathf.Lerp(_rotationCurrent.y, _rotationTarget.y, r);
            _rotationCurrent.x = Mathf.Lerp(_rotationCurrent.x, _rotationTarget.x, r);

            UpdateRotations();

            if (_target != null)
            {
                Vector3 targetPosition = _cameraOverShoulder ? _target.GetRotation().TransformPoint(_sO.GetCameraOverShoulderOffset()) : _target.transform.position;
                Quaternion targetRotation = _cameraOverShoulder ? Quaternion.LookRotation(_target.GetRotation().forward) : transform.rotation;

                transform.position = Vector3.Lerp(transform.position, targetPosition, Time.deltaTime * _sO.GetTargetFollowSpeedMove());
                transform.rotation = Quaternion.Lerp(transform.rotation, targetRotation, Time.deltaTime * _sO.GetTargetFollowSpeedRotate());
            }

            // Update smooth zoom
            Vector3 zoom = _cameraPivot.localPosition;
            _targetZoom = Mathf.Clamp(_targetZoom, _sO.GetZoomOut(), _sO.GetZoomIn());
            zoom.z = Mathf.Lerp(zoom.z, _targetZoom, Time.smoothDeltaTime * _sO.GetZoomTargetFollowSpeed());
            _cameraPivot.localPosition = zoom;
        }

        private void UpdateRotations()
        {
            horizontalTransform.localRotation = Quaternion.Euler(0f, _rotationCurrent.y, 0f);
            verticalTransform.localRotation = Quaternion.Euler(_rotationCurrent.x, 0f, 0f);
        }

        public void SetTarget(CharacterEntity value, bool instant)
        {
            _target = value;
            _mainCamera.transform.SetParent(_cameraPivot, Vector3.zero, Quaternion.identity, Vector3.one);

            if (instant)
            {
                if (_target != null)
                {
                    transform.position = _target.transform.position;
                }
            }
        }

        public void SetCustomPosition(Transform value)
        {
            _target = null;
            _mainCamera.transform.SetParent(value, Vector3.zero, Quaternion.identity, Vector3.one);
        }
        
        public void SetCustomPosition(Vector3 worldPosition)
        {
            _target = null;
            _mainCamera.transform.SetParent(null, worldPosition, Quaternion.identity, Vector3.one);
        }

        public void ReturnHome()
        {
            _mainCamera.transform.SetParent(_cameraPivot, Vector3.zero, Quaternion.identity, Vector3.one);
        }

        public void AddLook(Vector2 delta)
        {
            if (_cameraOverShoulder) return;
            float speed = _sO.GetLookSpeedMultiplier();
            _rotationTarget.y += delta.x * speed;
            _rotationTarget.x = Mathf.Clamp(_rotationTarget.x - (delta.y * speed), 0f, 80f);
        }

        public void AddZoom(float quantity)
        {
            _targetZoom += quantity;
        }

        public void SetZoom(float value)
        {
            Vector3 zoom = _cameraPivot.localPosition;
            zoom.z = _targetZoom = Mathf.Clamp(value, _sO.GetZoomOut(), _sO.GetZoomIn());
            _cameraPivot.localPosition = zoom;
        }

    }
}