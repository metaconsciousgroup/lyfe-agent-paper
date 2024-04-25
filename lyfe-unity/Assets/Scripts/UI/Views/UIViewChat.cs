using System;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using System.Linq;

[System.Serializable]
public class StringStringEvent : UnityEvent<string, string> { }


public class UIViewChat : UIView
{
    [Header(H_L + "View - Chat" + H_R)]
    [SerializeField] private int _maxMessages;
    [SerializeField] private InputField _inputField;
    [SerializeField] private Button _buttonSend;
    [SerializeField] private UIContent _content;
    [SerializeField] private CanvasGroup _canvasBackground;
    [SerializeField] private CanvasGroup _canvasGroupFooter;
    [Header("Channels")]
    [SerializeField] private UIContentElementChatChannel _defaultChannel;
    [SerializeField] private UIContent _contentChannels;

    [SerializeField] private StringStringEvent _onPostMessage;

    public bool IsChatInputFieldFocused => _inputField.isFocused;

    public string GetDefaultChannelId() => _defaultChannel.GetChannelId();

    protected override void OnGroupOpened()
    {

    }

    protected override void OnGroupClosed()
    {

    }

    private void Update()
    {
        // Should be removed from here and updated only on event basis
        UpdatePlayerInputBlocking();
    }

    private void LateUpdate()
    {
        UpdateLook();
    }


    private void UpdateLook()
    {
        bool isFocused = IsChatInputFieldFocused;
        _canvasGroupFooter.alpha = isFocused ? 1f : 0.5f;
        _canvasBackground.alpha = isFocused ? 1f : 0f;
    }

    public void Focus()
    {
        //Debug.Log("focus");
        _inputField.Select();
        _inputField.ActivateInputField();
    }

    public void Unfocus()
    {
        //Debug.Log("unfocus");
    }


    private void UpdatePlayerInputBlocking()
    {
        Player player = App.Instance.GetGame().GetPlayer();
        bool isFocused = IsChatInputFieldFocused;
        player.GetStateMovement().AlterBlock(GetIdentifier(), isFocused);
        player.GetStateMouseZoom().AlterBlock(GetIdentifier(), isFocused);
    }

    public void OnInputFieldValueChanged(string value)
    {
        _buttonSend.interactable = !string.IsNullOrWhiteSpace(value);
    }

    public void OnInputFieldSubmit(string message)
    {
        if (Input.GetKeyDown(KeyCode.Return))
        {
            if (PostMessage())
            {

            }
            else
            {
                _inputField.DeactivateInputField();
                EventSystem eventSystem = EventSystem.current;
                if (!eventSystem.alreadySelecting) eventSystem.SetSelectedGameObject(null);
                //Debug.Log("end end");
            }
        }
    }

    public void OnInputFieldEndEdit(string input)
    {

    }

    public void OnButtonSendClick()
    {
        PostMessage();
    }

    /// <summary>
    /// Adds chat message.
    /// </summary>
    /// <param name="chatMessageData"></param>
    public void AddMessage(ChatMessageData chatMessageData)
    {
        if (chatMessageData == null) return;

        string channelId = chatMessageData.channelId;

        if (GetOrCreateDirectChannel(channelId, out UIContentElementChatChannel channel))
        {
            ClampMessagesBefore(channel);

            _content.Create<UIContentElementChatMessage>()
                .SetData(channel, chatMessageData.user, chatMessageData.message)
                .UpdateVisibility(GetSelectedChannel());
        }
    }
    private void ClampMessagesBefore(UIContentElementChatChannel chatChannel)
    {
        if (chatChannel == null)
        {
            throw new ArgumentNullException(nameof(chatChannel));
        }
        // Get all chat messages
        UIContentElementChatMessage[] elements = _content.GetElements<UIContentElementChatMessage>(true);

        // Filter messages that belong to the specified channel
        var channelMessages = elements.Where(element => element.GetChannel().GetChannelId() == chatChannel.GetChannelId()).ToArray();

        int removeCount = Mathf.Max((channelMessages.Length + 1) - _maxMessages, 0);

        for (int i = 0; i < removeCount; i++)
        {
            Destroy(channelMessages[i].gameObject);
        }
    }

    /// <summary>
    /// Get or create chat channel.
    /// </summary>
    /// <param name="channelId"></param>
    /// <param name="channel">Optional result channel.</param>
    /// <returns>Returns true if channel found or created.</returns>
    private bool GetOrCreateDirectChannel(string channelId, out UIContentElementChatChannel channel)
    {
        channel = null;

        if (!string.IsNullOrEmpty(channelId))
        {
            // Requested channel is default channel
            if (_defaultChannel.GetChannelId() == channelId)
            {
                channel = _defaultChannel;
            }

            // Requested channel is something else
            else
            {
                UIContentElementChatChannel[] existingChannels = _contentChannels.GetElements<UIContentElementChatChannel>(true);
                // Try to find existing channel
                foreach (UIContentElementChatChannel i in existingChannels)
                {
                    if (i.GetChannelId() == channelId)
                    {
                        channel = i;
                        return true;
                    }
                }

                // Check if target channel is valid for existing character
                if (!App.Instance.GetGame().GetCharacters().GetById(channelId, out CharacterEntity character))
                {
                    Debug.LogWarning($"Target channel id '{channelId}' could not be resolved by existing character, skipping..");
                    return false;
                }
                channel = _contentChannels.Create<UIContentElementChatChannel>();
                channel.SetChannel(channelId, character.GetReadyPlayerMeAvatarRenderer().GetUrl());
            }
        }

        return channel != null;
    }

    private bool PostMessage()
    {
        string message = _inputField.text;
        string channelId = GetSelectedChannel().GetChannelId();
        _inputField.text = string.Empty;
        return PostMessage(message, channelId);
    }

    private bool PostMessage(string message, string channelId)
    {
        Focus();

        if (message != null)
        {
            message = message.Trim();

            if (!string.IsNullOrWhiteSpace(message))
            {
                _onPostMessage?.Invoke(message, channelId);
                return true;
            }
        }

        return false;
    }

    /// <summary>
    /// Returns currently selected channel.
    /// </summary>
    /// <returns></returns>
    private UIContentElementChatChannel GetSelectedChannel() => _contentChannels.GetSelection().GetSelected<UIContentElementChatChannel>();

    /// <summary>
    /// Updates all chat message visibility considering current chat channel.
    /// </summary>
    private void UpdateMessageVisibilityFromCurrentSelectedChannel()
    {
        UIContentElementChatChannel selectedChannel = GetSelectedChannel();
        foreach (UIContentElementChatMessage chatMessage in _content.GetElements<UIContentElementChatMessage>(true))
        {
            chatMessage.UpdateVisibility(selectedChannel);
        }
    }

    public void OnChatChannelSelectionChanged(UIContentSelection.EventData eventData)
    {
        UpdateMessageVisibilityFromCurrentSelectedChannel();
    }
}