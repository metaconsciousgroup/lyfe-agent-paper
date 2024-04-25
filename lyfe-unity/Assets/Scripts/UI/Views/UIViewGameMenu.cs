using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UIViewGameMenu : UIView
{
    protected override void OnGroupOpened()
    {
        
    }

    protected override void OnGroupClosed()
    {
        
    }

    /// <summary>
    /// Called from button inspector click callback.
    /// </summary>
    public void OnButtonContinue()
    {
        ToggleGroup(false);
    }
    
    /// <summary>
    /// Called from button inspector click callback.
    /// </summary>
    public void OnButtonSettings()
    {
        App.Instance.GetUI().GetView<UIViewSettings>().OpenGroup();
    }
    
    /// <summary>
    /// Called from button inspector click callback.
    /// </summary>
    public void OnButtonQuit()
    {
        App.Instance.GetGame().GetNetwork().StopClient();
    }

    public override bool Escape()
    {
        return ToggleGroup(false);
    }
}
