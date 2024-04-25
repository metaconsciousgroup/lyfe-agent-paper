using Sirenix.OdinInspector;
using UnityEngine;

public class UIContentElementCharacter : UIContentElement
{
    [SerializeField] private ReadyPlayerMeAvatarRendererUI _avatarRenderer;
    [SerializeField] private GameObject _selection;

    [ReadOnly, ShowInInspector]
    private InDataCharacter _data;

    public InDataCharacter GetData() => _data;
    

    protected override bool CanSelect()
    {
        return true;
    }

    public override void SetIsSelected(bool isSelected)
    {
        base.SetIsSelected(isSelected);
        _selection.SetActive(isSelected);
    }

    public void SetData(InDataCharacter value)
    {
        _data = value;
        _avatarRenderer.Load(value.modelPath);
    }

    protected override void OnSelect(int layer)
    {
        base.OnSelect(layer);
        if(layer == 0) App.Instance.GetAudio().GetButtonClick().Play();
    }
}
