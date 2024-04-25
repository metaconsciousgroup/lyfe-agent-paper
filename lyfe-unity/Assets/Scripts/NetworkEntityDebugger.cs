using TMPro;
using UnityEngine;

public class NetworkEntityDebugger : BaseMonoBehaviour
{
    [SerializeField] private NetworkEntity _target;
    [SerializeField] private TMP_Text _tmp;

    protected override void Start()
    {
        base.Start();
        UpdateLook();
    }

    private void LateUpdate()
    {
        UpdateLook();
    }

    private void Clear()
    {
        _tmp.Clear();
        gameObject.SetActive(false);
    }

    public void SetTarget(NetworkEntity value)
    {
        _target = value;
        if (UpdateLook())
        {
            gameObject.SetActive(true);
        }
    }

    private bool UpdateLook()
    {
        if (_target == null)
        {
            Clear();
            return false;
        }

        if (!_target.GetGizmoDebuggerInfo(out string text))
        {
            Clear();
            return false;
        }
        
        _tmp.SetText(text);
        return true;
    }

    
}
