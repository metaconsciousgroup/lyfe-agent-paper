using Sirenix.OdinInspector;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;

public abstract class UIViewLobby : UIView
{
    [Header(H_L + "View - Lobby" + H_R)]
    [ReadOnly, ShowInInspector] private bool _isLoading;
    [SerializeField] private UICanvasGroupToggle _canvasGroupPanelToggle;
    [SerializeField] private Button _buttonStart;
    [SerializeField] private GameObject _loading;
    [Space]
    [SerializeField] private GameObject _network;
    [SerializeField] private TMP_InputField _inputFieldNetwork;
    [Space]
    [SerializeField] private GameObject _portStandalone;
    [SerializeField] private TMP_InputField _inputFieldPortStandalone;
    [Space]
    [SerializeField] private GameObject _portWeb;
    [SerializeField] private TMP_InputField _inputFieldPortWeb;
    [Space]
    [SerializeField] private TMP_InputField _inputFieldUsername;
    [SerializeField] private bool _requiredSelectedCharacter;
    [SerializeField] private bool _autoSelectFirstAppearance;
    [SerializeField] private UIContent _contentAppearance;

    [SerializeField] private UnityEventLoginRequest _onButtonStart;

    protected abstract string GetSceneOverride();

    protected override void Awake()
    {
        base.Awake();

        ConstructLobby();
        Clear();
    }

    public void OnButtonStart()
    {
        Debug.Log($"{GetType().Name}.OnButtonStart");
        if (GetLoginRequest(out UnityEventLoginRequest.Data data))
        {
            TogglePanelInteractable(false);
            SetIsLoading(true);
            _onButtonStart?.Invoke(data);
        }
        else
        {
            Debug.LogWarning("Failed to collection login request");
        }
    }

    public void OnContentSelectionCharactersChanged(UIContentSelection.EventData eventData)
    {
        UpdateLook();
    }

    public void OnInputFieldValueChanged(string value)
    {
        UpdateLook();
    }

    private void ConstructLobby()
    {
        _contentAppearance.Clear();

        SOAppConfig config = App.Instance.GetConfig();
        SOReadyPlayerMeAvatars avatars = config.GetReadyPlayerMe().GetAvatars();
        int maxAvatars = config.GetEnvironment().GetLobby().maximumAppearances;

        List<SOReadyPlayerMeAvatar> avatarWhitelist = maxAvatars < 0 ? new List<SOReadyPlayerMeAvatar>(avatars.GetValues()) : avatars.GetRandomValues(maxAvatars);
        avatarWhitelist.Shuffle();

        foreach (SOReadyPlayerMeAvatar avatar in avatarWhitelist)
        {
            InDataCharacter characterData = new()
            {
                modelPath = avatar.GetUrl()
            };
            UIContentElementCharacter element = _contentAppearance.Create<UIContentElementCharacter>();
            element.SetData(characterData);
        }

        ClearAppearanceSelection();
    }

    private List<int> SelectRandomIndex(int A, int B)
    {
        int[] array = new int[A];
        List<int> result = new List<int>(B);

        for (int i = 0; i < A; i++)
        {
            array[i] = i;
        }

        // Randomly select B unique integers
        for (int i = 0; i < B; i++)
        {
            int j = Random.Range(i, A);
            int temp = array[i];
            array[i] = array[j];
            array[j] = temp;
            result.Add(array[i]);
        }

        return result;
    }

    private void ClearAppearanceSelection()
    {
        _contentAppearance.GetSelection().ClearSelection();

        if (_autoSelectFirstAppearance)
        {
            UIContentElementCharacter[] characters = _contentAppearance.GetElements<UIContentElementCharacter>(true);
            int length = characters.Length;
            if (length > 0)
            {
                characters[0].Select(-1);
            }
        }
    }

    public bool GetFieldPortStandalone(out ushort portStandalone)
    {
        string text = _inputFieldPortStandalone.text;
        if (ushort.TryParse(text, out portStandalone)) return true;

        return true;
    }

    public bool GetFieldPortWeb(out ushort portWeb)
    {
        string text = _inputFieldPortWeb.text;
        if (ushort.TryParse(text, out portWeb)) return true;
        Debug.LogWarning($"Invalid web port '{text}'");
        return true;
    }

    protected bool GetLoginRequest(out UnityEventLoginRequest.Data data)
    {
        Debug.Log($"{GetType().Name}.GetLoginRequest");
        data = null;
        UIContentElementCharacter selectedCharacter = _contentAppearance.GetSelection().GetSelected<UIContentElementCharacter>();

        if (!GetCharacterData(selectedCharacter, out InDataCharacter characterData))
        {
            Debug.LogWarning("Failed to get selected appearance");
            return false;
        }

        Debug.Log("Getting port numbers");
        if (!GetFieldPortStandalone(out ushort portStandalone)) return false;
        Debug.Log($"Standalone port: {portStandalone}");
        if (!GetFieldPortWeb(out ushort portWeb)) return false;
        Debug.Log($"Web port: {portWeb}");

        if (portStandalone == portWeb)
        {
            Debug.LogWarning("Ports cannot have the same value");
        }

        string network = _inputFieldNetwork.text;
        string username = _inputFieldUsername.text;
        Debug.Log($"Network: {network} Username: {username}");

        data = new UnityEventLoginRequest.Data(
            network,
            portStandalone,
            portWeb,
            selectedCharacter == null,
            username,
            characterData,
            GetSceneOverride());
        Debug.Log($"Data: {data}");
        return true;
    }

    private bool GetCharacterData(UIContentElementCharacter selectedCharacter, out InDataCharacter characterData)
    {
        characterData = null;
        if (selectedCharacter != null) characterData = selectedCharacter.GetData();

        if (_requiredSelectedCharacter && characterData == null) return false;

        if (characterData == null)
        {
            characterData = new InDataCharacter()
            {
                modelPath = string.Empty
            };
        }
        return true;
    }


    public virtual void Clear()
    {
        NetworkData data = App.Instance.GetGame().GetNetwork().GetNetworkDefaults();

        _inputFieldNetwork.text = data.hostName;
        _inputFieldPortStandalone.text = data.portStandalone;
        _inputFieldPortWeb.text = data.portWeb;
        _inputFieldUsername.text = data.username;

        ClearAppearanceSelection();
        UpdateLook();
        TogglePanelInteractable(true);
        SetIsLoading(false);
    }

    protected virtual void UpdateLook()
    {
        SOUIViewLobby lobbyConfig = App.Instance.GetConfig().GetEnvironment().GetLobby();

        _network.SetActive(lobbyConfig.showHostName);
        _portStandalone.SetActive(lobbyConfig.showPortStandalone);
        _portWeb.SetActive(lobbyConfig.showPortWeb);

        _canvasGroupPanelToggle.gameObject.SetActive(CanPanelBeVisible());
        _buttonStart.interactable = CanClickButton();
    }

    protected virtual bool CanClickButton()
    {
        string username = _inputFieldUsername.text;
        bool usernameValid = !string.IsNullOrWhiteSpace(username);
        bool characterValid = !_requiredSelectedCharacter || _contentAppearance.GetSelection().IsSelected();

        bool valid = usernameValid && characterValid;

        return valid;
    }

    protected virtual bool CanPanelBeVisible()
    {
        return true;
    }

    protected void TogglePanelInteractable(bool isActive)
    {
        _canvasGroupPanelToggle.SetOn(isActive);
    }

    public void SetNetworkAddress(string networkAddress)
    {
        Debug.Log($"{GetType().Name}.SetNetworkAddress: {networkAddress}");
        _inputFieldNetwork.text = networkAddress;
    }

    public void SetIsLoading(bool value)
    {
        _isLoading = value;
        _buttonStart.gameObject.SetActive(!_isLoading);
        _loading.SetActive(_isLoading);
    }
}
