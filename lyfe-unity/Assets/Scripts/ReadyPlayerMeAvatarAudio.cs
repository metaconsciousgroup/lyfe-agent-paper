using ReadyPlayerMe.Core;
using Sirenix.OdinInspector;
using UnityEngine;

public class ReadyPlayerMeAvatarAudio : BaseMonoBehaviour
{
    [SerializeField, ReadOnly] private OutfitGender _outfitGender;
    [SerializeField] private CharacterEntity _character;
    [Header(H_L + "Emotes" + H_R)]
    [SerializeField] private AudioPlayer _audioGuitar;
    [SerializeField] private AudioPlayer _audioWaveMale;
    [SerializeField] private AudioPlayer _audioWaveFemale;
    [Header(H_L + "Movement" + H_R)]
    [SerializeField] private AudioPlayer _audioFootstep;
    
    private ReadyPlayerMeAvatar _avatar;
    private AudioPlayerEntry _previousEmote = null;

    private float GetCharacterSpeed() => _character.GetVelocity().GetSpeed();
    
#if UNITY_EDITOR
    protected override void Reset()
    {
        base.Reset();
        _outfitGender = OutfitGender.None;
    }
#endif

    private void OnAvatarAnimationWalkFootstep()
    {
        PlayFootstep();
    }
    
    private void OnAvatarAnimationRunFootstep()
    {
        PlayFootstep();
    }

    private void PlayFootstep()
    {
        float speed = GetCharacterSpeed();
        if (speed > 0.01f)
        {
            if (_audioFootstep.Play(out AudioPlayerEntry entry))
            {
                float percentage = Mathf.InverseLerp(0f, _character.GetSO().GetSprint(), GetCharacterSpeed());
                float maxVolume = _audioFootstep.GetPrefab().GetSource().volume;
                float minVolume = maxVolume * 0.1f;
                entry.GetSource().volume = Mathf.Lerp(minVolume, maxVolume, percentage);
            }
        }
    }

    public void PlayEmote(SOEmote emote)
    {
        StopCurrentEmote();
        if (emote == null) return;
        
        switch (emote.GetKind())
        {
            case EmoteKind.Wave:
            {
                switch (_outfitGender)
                {
                    case OutfitGender.Neutral:
                    case OutfitGender.Masculine:
                    {
                        if (_audioWaveMale.Play(out AudioPlayerEntry entry)) _previousEmote = entry;
                        break;
                    }
                    case OutfitGender.Feminine:
                    {
                        if (_audioWaveFemale.Play(out AudioPlayerEntry entry)) _previousEmote = entry;
                        break;
                    }
                }
                break;
            }
            case EmoteKind.Point:
            {

                break;
            }
            case EmoteKind.Guitar:
            {
                if (_audioGuitar.Play(out AudioPlayerEntry entry)) _previousEmote = entry;
                break;
            }
            case EmoteKind.Laugh:
            {

                break;
            }
        }
    }

    public void StopCurrentEmote()
    {
        if (_previousEmote == null) return;
        _previousEmote.Stop();
    }

    public void SetAvatar(ReadyPlayerMeAvatar value)
    {
        _avatar = value;
        if (_avatar != null)
        {
            _outfitGender = _avatar.GetAvatarData().AvatarMetadata.OutfitGender;
        }
        AlterAvatarEventSubscriptions(true);
    }
    
    public void ClearAvatar()
    {
        AlterAvatarEventSubscriptions(false);
        _outfitGender = OutfitGender.None;
        _avatar = null;
    }
    
    private void AlterAvatarEventSubscriptions(bool alter)
    {
        if (_avatar == null) return;
        _avatar.onAnimationWalkFootstep.AlterListener(OnAvatarAnimationWalkFootstep, alter);
        _avatar.onAnimationRunFootstep.AlterListener(OnAvatarAnimationRunFootstep, alter);
    }
}
