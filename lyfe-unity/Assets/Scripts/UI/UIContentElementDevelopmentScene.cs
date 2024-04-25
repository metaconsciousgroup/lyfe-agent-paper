using Sirenix.OdinInspector;
using TMPro;
using UnityEngine;

public class UIContentElementDevelopmentScene : UIContentElement
{
    [Header("Development Scene")]
    [SerializeField] private SODevelopmentScene _sO;

    [Space] [SerializeField] private GameObject _selection;
    [SerializeField] private TMP_Text _tmpTitle;
    [SerializeField] private UIImage _image;

    public SODevelopmentScene GetSO() => _sO;
    
#if UNITY_EDITOR
    protected override void OnValidate()
    {
        base.OnValidate();
        UpdateLook();
    }
#endif
    
    protected override bool CanSelect() => true;

    public override void SetIsSelected(bool isSelected)
    {
        base.SetIsSelected(isSelected);
        if(_selection != null) _selection.SetActive(isSelected);
    }

    protected override void Awake()
    {
        base.Awake();
        UpdateLook();
    }

    [Button]
    private void UpdateLook()
    {
        if(_tmpTitle != null) _tmpTitle.SetText(_sO == null ? null : _sO.GetTitle());
        if(_image != null) _image.SetSprite(_sO == null ? null : _sO.GetImage());
    }
}
