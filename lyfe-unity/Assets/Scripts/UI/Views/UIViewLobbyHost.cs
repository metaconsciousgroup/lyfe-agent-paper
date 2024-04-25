using Sirenix.OdinInspector;
using UnityEngine;
using TMPro;

public class UIViewLobbyHost : UIViewLobby
{
    [Header(H_L + "View - Lobby - Server" + H_R)]
    [SerializeField] private TMP_Text _tmoPythonConnection;
    [SerializeField] private TMP_InputField _inputFieldLocation;
    [SerializeField] private GameObject _panelOverrideScene;
    
    [ReadOnly, ShowInInspector] private PythonSendInGame _pythonGameData;
    [ReadOnly, ShowInInspector] private SOScene _overrideFallbackScene;


    protected override string GetSceneOverride() =>
        _overrideFallbackScene == null ? null : _overrideFallbackScene.GetName();

    protected override void Awake()
    {
        base.Awake();
    }

    protected override void OnGroupOpened()
    {
        Clear();
    }

    protected override void OnGroupClosed()
    {
        Clear();
    }

    public void SetData(PythonSendInGame value)
    {
        _pythonGameData = value;
        UpdateLook();
    }

    protected override void UpdateLook()
    {
        base.UpdateLook();
        if(_panelOverrideScene != null) _panelOverrideScene.SetActive(_pythonGameData == null ? false : !_pythonGameData.fromPython);
        if(_inputFieldLocation != null) _inputFieldLocation.text = _pythonGameData == null ? string.Empty : _pythonGameData.scene.title;
        if(_tmoPythonConnection != null)
        {
            bool on = _pythonGameData?.fromPython ?? false;
            string value = on ? "ONLINE".Color(Color.green) : "OFFLINE".Color(Color.red);
            _tmoPythonConnection.text = $"Python: {value}";
        }
    }

    protected override bool CanPanelBeVisible()
    {
        return _pythonGameData != null;
    }

    protected override bool CanClickButton()
    {
        bool locationValid = !string.IsNullOrEmpty(_inputFieldLocation.text);
        return locationValid && base.CanClickButton();
    }

    public void OnButtonBack()
    {
        ToggleGroup(false);
        App.Instance.GetUI().GetView<UIViewAppEnvironment>().ToggleGroup(true);
    }


    public override void Clear()
    {
        _inputFieldLocation.text = string.Empty;
        _pythonGameData = null;
        base.Clear();
    }

    public void OnSelectionOverrideFallbackScene(UIContentSelection.EventData eventData)
    {
        _overrideFallbackScene = null;
        
        if (eventData.current == null) return;

        UIContentElementDevelopmentScene element = (UIContentElementDevelopmentScene)eventData.current;
        _overrideFallbackScene = element.GetSO().GetScene();
    }
    

    
}