using UnityEngine;

public class UIViewAppEnvironment : UIView
{
    protected override void OnGroupOpened()
    {
        
    }

    protected override void OnGroupClosed()
    {
        
    }

    public void OnButtonHost()
    {
        Debug.Log($"{GetType().Name}.OnButtonHost");
        ToggleGroup(false);
        App.Instance.GetGame().StartAsServer();
    }
    
    public void OnButtonClient()
    {
        Debug.Log($"{GetType().Name}.OnButtonClient");
        ToggleGroup(false);
        App.Instance.GetGame().StartAsClient();
    }
}
