using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class UIEmoteButton : UIMonoBehaviour, IPointerEnterHandler, IPointerExitHandler
{
    [SerializeField] private UIViewEmoteSelector _selector;
    [Space]
    [SerializeField] private SOEmote _sO;
    [SerializeField] private UIButton _button;
    [SerializeField] private Image _imageIcon;
    [SerializeField] private AudioPlayer _audioHover;
    
#if UNITY_EDITOR
    protected override void Reset()
    {
        base.Reset();
        _button = GetComponent<UIButton>();
    }

    protected override void OnValidate()
    {
        base.OnValidate();
        if (_imageIcon != null)
        {
            _imageIcon.rectTransform.rotation = Quaternion.Euler(Vector3.zero);
        }
    }
#endif

    protected override void Awake()
    {
        base.Awake();
        UpdateLook();
    }
    
    public void OnPointerEnter(PointerEventData eventData)
    {
        if (_audioHover == null || !_button.interactable) return;
        _audioHover.Play();
    }

    public void OnPointerExit(PointerEventData eventData)
    {
        
    }

    private void UpdateLook()
    {
        _button.interactable = _sO != null;
        _imageIcon.SetSprite(_sO == null ? null : _sO.GetSprite());
    }

    public void SetEmote(SOEmote value)
    {
        _sO = value;
        UpdateLook();
    }

    public void OnButtonClick()
    {
        if (_selector.SelectEmote(_sO))
        {
            _selector.ToggleGroup(false);
        }
    }

    
}
