using UnityEngine;

public class UIViewMinimap : UIView
{
    [SerializeField] private Transform _cameraPivot;
    [Space]
    [SerializeField] private Transform _targetPosition;
    [SerializeField] private bool _rotateCameraPivot;
    [SerializeField] private Transform _targetRotation;
    [SerializeField] private RectTransform _arrow;
    

    protected override void OnGroupOpened()
    {
        ToggleWorldPivot(true);
    }

    protected override void OnGroupClosed()
    {
        ToggleWorldPivot(false);
    }

    private void Update()
    {
        UpdateWorldPivot();
    }

    public UIViewMinimap SetTargetPosition(Transform value)
    {
        _targetPosition = value;
        return this;
    }
    
    public UIViewMinimap SetTargetRotation(Transform value)
    {
        _targetRotation = value;
        return this;
    }

    public void ClearTargets()
    {
        _targetPosition = null;
        _targetRotation = null;
    }

    private void UpdateWorldPivot()
    {
        if (_cameraPivot == null) return;
        
        if (_targetPosition != null)
        {
            _cameraPivot.position = _targetPosition.position;
        }

        if (_targetRotation != null)
        {
            if (_rotateCameraPivot)
            {
                _cameraPivot.rotation = _targetRotation.rotation;
                _arrow.localEulerAngles = Vector3.zero;
            }
            else
            {
                _cameraPivot.rotation = Quaternion.identity;
                _arrow.localEulerAngles = new Vector3(0f, 0f, -_targetRotation.eulerAngles.y);
            }
            
        }
    }

    private void ToggleWorldPivot(bool isActive)
    {
        if(_cameraPivot != null) _cameraPivot.gameObject.SetActive(isActive);
    }
}
