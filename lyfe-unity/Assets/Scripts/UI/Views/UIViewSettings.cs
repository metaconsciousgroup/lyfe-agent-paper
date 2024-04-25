using TMPro;
using UnityEngine;
using UnityEngine.UI;

public class UIViewSettings : UIView
{
    [Header(H_L + "Settings" + H_R)]
    [SerializeField] private bool _debug;
    [SerializeField] private SOAppSettings _appSettings;
    [SerializeField] private TMP_Text _tmpHudScaleValue;
    [SerializeField] private TMP_Text _tmpFieldOfView;
    [SerializeField] private Slider _sliderCameraZoom;
    [SerializeField] private UIViewFPS _viewFps;


    protected override void Awake()
    {
        base.Awake();

        // Camera zoom
        SOPlayerCamera playerCamera = _appSettings.GetPlayerCamera();
        _sliderCameraZoom.minValue = playerCamera.GetZoomOut();
        _sliderCameraZoom.maxValue = playerCamera.GetZoomIn();
        _sliderCameraZoom.value = App.Instance.GetGame().GetPlayer().GetCamera().GetCurrentZoom();
        _sliderCameraZoom.onValueChanged.AddListener(OnSliderCameraZoom);
    }

    protected override void OnGroupOpened()
    {
        
    }

    protected override void OnGroupClosed()
    {
        
    }


    public void OnSliderHudScaleChanged(float value)
    {
        if(_debug)
            Debug.Log($"{GetType().Name}.OnSliderHudScaleChanged({value})");
        
        _tmpHudScaleValue.SetText(value);
        App.Instance.GetUI().SetReferenceResolutionY(value);
    }
    
    public void OnSliderFieldOfView(float value)
    {
        if(_debug)
            Debug.Log($"{GetType().Name}.OnSliderFieldOfView({value})");
        
        _tmpFieldOfView.SetText(value);
        App.Instance.GetGame().GetPlayer().GetCamera().GetMainCamera().fieldOfView = value;
    }
    
    private void OnSliderCameraZoom(float value)
    {
        if(_debug)
            Debug.Log($"{GetType().Name}.OnSliderCameraZoom({value})");
        
        App.Instance.GetGame().GetPlayer().GetCamera().SetZoom(value);
    }

    public void OnShowFpsToggle(bool isOn)
    {
        _viewFps.ToggleGroup(isOn);
    }
    
    public override bool Escape()
    {
        return ToggleGroup(false);
    }
}
