using Sirenix.OdinInspector;
using UnityEngine;

public class UIContentElementChatChannel : UIContentElement
{
    [Header(H_L + "Chat Channel" + H_R)]
    [TextArea(3, 6)]
    [SerializeField] private string _channelId;
    [SerializeField] private ReadyPlayerMeAvatarRendererUIRawImage _avatarRenderer;
    [SerializeField] private GameObject _selection;
    
    protected override bool CanSelect() => true;

    public override void SetIsSelected(bool isSelected)
    {
        base.SetIsSelected(isSelected);
        if(_selection != null) _selection.SetActive(isSelected);
    }

    /// <summary>
    /// Returns unique channel identifier.
    /// </summary>
    /// <returns></returns>
    public string GetChannelId() => _channelId;

    /// <summary>
    /// Sets current channel from game character, this will result in direct message channel, where channelId is character user id.
    /// </summary>
    /// <param name="character"></param>
    public void SetChannel(string channelId, string avatarIconUrl)
    {
        _channelId = channelId;
        _avatarRenderer.Load(avatarIconUrl);
    }
}
