using Sirenix.OdinInspector;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class UIContentElementNearByArea : UIContentElement
{
    [Header(H_L + "Proximity Character" + H_R)]
    [ReadOnly, ShowInInspector] private LyfeCreatorWorldArea _area;
    [SerializeField] private TMP_Text _textAreaTitle;

    public LyfeCreatorWorldArea GetCharacter() => _area;

    protected override bool CanSelect() => false;

    public void SetArea(LyfeCreatorWorldArea area)
    {
        _area = area;
        _textAreaTitle.text = area.GetKey();
    }
}