using Sirenix.OdinInspector;
using UnityEngine;

public class UICanvasGroupToggle : UIMonoBehaviour
{
    [SerializeField] private bool _isOn;
    [SerializeField] private CanvasGroup _canvasGroup;
    [SerializeField] private CanvasGroupData _on;
    [SerializeField] private CanvasGroupData _off;

#if UNITY_EDITOR
    protected override void Reset()
    {
        base.Reset();
        _isOn = true;
        _canvasGroup = GetComponent<CanvasGroup>();
        _on = new CanvasGroupData()
        {
            alpha = 1f,
            interactable = true,
            blocksRaycasts = true,
            ignoreParentGroups = false
        };
        _off = new CanvasGroupData()
        {
            alpha = 0.5f,
            interactable = false,
            blocksRaycasts = false,
            ignoreParentGroups = false
        };
    }

    protected override void OnValidate()
    {
        base.OnValidate();
        UpdateSettings();
    }
#endif

    public void SetOn(bool value)
    {
        _isOn = value;
        UpdateSettings();
    }

    [Button]
    public void ToggleOn()
    {
        SetOn(!_isOn);
    }

    private void UpdateSettings()
    {
        SetSettings(_isOn ? _on : _off);
    }
    
    private void SetSettings(CanvasGroupData data)
    {
        if (data == null) return;
        if (_canvasGroup == null) return;

        _canvasGroup.alpha = data.alpha;
        _canvasGroup.interactable = data.interactable;
        _canvasGroup.blocksRaycasts = data.blocksRaycasts;
        _canvasGroup.ignoreParentGroups = data.ignoreParentGroups;
    }
}
