using Sirenix.OdinInspector;
using TMPro;
using UnityEngine;

public class UIViewInfoPopup : UIView
{
    [Header(H_L + "View - Info Popup" + H_R)]
    [SerializeField] private TMP_Text _tmpTitle;
    [SerializeField] private TMP_Text _tmpDescription;
    [SerializeField] private UIContent _contentButtons;
    
    protected override void OnGroupOpened()
    {
        
    }

    protected override void OnGroupClosed()
    {
        
    }
    
#if UNITY_EDITOR
    [Button]
    public void TestOne()
    {
        Show(
            "This is a test title.",
            "This is a very long test description message.",
            InfoPopupButtonData.From("Close")
        );
    }
    
    [Button]
    public void TestTwo()
    {
        Show(
            "This is a test title.",
            "This is a very long test description message.",
            InfoPopupButtonData.From("Yes"), InfoPopupButtonData.From("No")
        );
    }
#endif
    
    /// <summary>
    /// Show info popup.
    /// </summary>
    /// <param name="title">Popup title.</param>
    /// <param name="description">Popup description.</param>
    /// <param name="buttons">Popup buttons.</param>
    public void Show(string title, string description, params InfoPopupButtonData[] buttons)
    {
        // Already open
        if (GetGroup().GetIdentifier().Contains())
        {
            return;
        }

        int buttonCount = buttons?.Length ?? 0;
        Debug.Log($"{GetType().Name}.Show({title}, {description}, buttonCount:{buttonCount})");
        
        Clear();
        _tmpTitle.SetText(title);
        _tmpDescription.SetText(description);
        if (buttons != null)
        {
            foreach (InfoPopupButtonData buttonData in buttons)
            {
                _contentButtons.Create<UIContentElementInfoPopupButton>().SetData(this, buttonData);
            }
        }
        ToggleGroup(true);
    }

    public void Clear()
    {
        _tmpTitle.Clear();
        _tmpDescription.Clear();
        _contentButtons.Clear();
    }
}
