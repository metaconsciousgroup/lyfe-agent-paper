using FishNet.Managing.Scened;
using UnityEngine;
using UnityEngine.UI;

public class UIViewLoadingScreen : UIView
{
    [SerializeField] private Slider _sliderLoadingBar;
    
    protected override void OnGroupOpened()
    {
        
    }

    protected override void OnGroupClosed()
    {
        
    }

    public void OnNetworkLoadStart(SceneLoadStartEventArgs args)
    {
        OpenGroup();
    }

    public void OnNetworkLoadPercentChange(SceneLoadPercentEventArgs args)
    {
        SetLoadingBar(args.Percent);
    }
    
    public void OnNetworkLoadEnd(SceneLoadEndEventArgs args)
    {
        CloseGroup();
    }

    public void SetLoadingBar(float value)
    {
        _sliderLoadingBar.value = value;
    }
}
