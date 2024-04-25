using Sirenix.OdinInspector;
using TMPro;
using UnityEngine;

public class UIContentElementInfoPopupButton : UIContentElement
{
    [Header(H_L + "Element - Info Popup Button" + H_R)]
    [SerializeField] private TMP_Text _tmpTitle;
    [ReadOnly, ShowInInspector] private InfoPopupButtonData _buttonData;
    private UIViewInfoPopup _view;
    
    protected override bool CanSelect() =>  true;

    public void SetData(UIViewInfoPopup view, InfoPopupButtonData value)
    {
        _view = view;
        _buttonData = value;
        _tmpTitle.SetText(_buttonData == null ? string.Empty : _buttonData.title);
    }

    protected override void OnSelect(int layer)
    {
        base.OnSelect(layer);
        if (_buttonData == null) return;
        _buttonData.onClick?.Invoke();
        if(_buttonData.autoCloseWindowOnClick) _view.CloseGroup();
    }
}
