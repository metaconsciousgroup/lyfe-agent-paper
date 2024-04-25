using Sirenix.OdinInspector;
using UnityEngine;

public class UIContentElementNearByCharacter : UIContentElement
{
    [Header(H_L + "Proximity Character" + H_R)]
    [ReadOnly, ShowInInspector] private CharacterEntity _character;
    [SerializeField] private ReadyPlayerMeAvatarRendererUIRawImage _avatarRenderer;

    public CharacterEntity GetCharacter() => _character;

    protected override bool CanSelect() => false;

    public void SetCharacter(CharacterEntity character)
    {
        _character = character;
        _avatarRenderer.Load(character.GetReadyPlayerMeAvatarRenderer().GetUrl());
    }
}
