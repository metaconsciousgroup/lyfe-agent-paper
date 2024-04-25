using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.UI;

public class UIContentElementChatMessage : UIContentElement
{
    [Header(H_L + "Chat Message" + H_R)]
    [SerializeField] private Text _textMessage;
    [SerializeField] private Color _colorUsername;

    [ReadOnly, ShowInInspector] private UIContentElementChatChannel _channel;
    
    [ReadOnly, ShowInInspector] private string _message;

    protected override bool CanSelect() => false;
    
    public UIContentElementChatChannel GetChannel() => _channel;

    public UIContentElementChatMessage SetData(UIContentElementChatChannel channel, UserEntity user, string message)
    {
        _channel = channel;
        _message = message;
        _textMessage.text = $"[{user.Username.GetValue().Color(_colorUsername)}] says: {_message}";
        return this;
    }

    public void UpdateVisibility(UIContentElementChatChannel currentChannel)
    {
        gameObject.SetActive(_channel == currentChannel);
    }

}
