using System.Collections;
using UnityEngine;
using ReadyPlayerMe.Core;
using Sirenix.OdinInspector;
using UnityEngine.Events;

public class ReadyPlayerMeAvatarRenderer : BaseMonoBehaviour, ICharacterLookDestination
{
    [ReadOnly, ShowInInspector] private string _url;
    [SerializeField] private SOValueString _layerMask;
    [SerializeField] private UnityEvent _onLoadCompleted;
    [SerializeField] private UnityEventString _onUrlChanged;
    [SerializeField] private CharacterEntity _character;
    [SerializeField] private ReadyPlayerMeAvatarAudio _audio;
    [SerializeField] private SOPrefabs _prefabs;
    
    [ReadOnly, ShowInInspector] private ReadyPlayerMeAvatar _avatarInstance;
    
    private static readonly int AnimatorPropertyMoveSpeed = Animator.StringToHash("MoveSpeed");
    private static readonly int AnimatorPropertyEmote = Animator.StringToHash("Emote");
    private static readonly int AnimatorPropertyEmoteTrigger = Animator.StringToHash("EmoteTrigger");

    private int _emoteId = 0;
    [SerializeField] private UnityEvent<int> _onEmote;

    private Smartphone _smartphone;
    private int _emoteActivityCounter = 0;

    public string GetUrl() => _url;
    
    public bool GetLookAtDestinationPoint(out Vector3 point)
    {
        point = Vector3.zero;
        if (_avatarInstance == null) return false;
        return _avatarInstance.GetLookAtDestinationPoint(out point);
    }

    public bool GetAvatarInstance(out ReadyPlayerMeAvatar instance)
    {
        instance = _avatarInstance;
        return instance != null;
    }

    public void LoadAvatar(string url)
    {
        if (_url == url) return;
        ClearAvatar();
        _url = url;
        _onUrlChanged.Invoke(url);
        
        App.Instance.GetReadyPlayerMeManager().GetAvatars().LoadAvatar(url, OnCompleted, OnProgressChanged, OnFailed);

        void OnCompleted(ReadyPlayerMeAvatar avatarInstance)
        {
            _avatarInstance = avatarInstance;
            
            avatarInstance.transform.SetParent(transform, Vector3.zero, Quaternion.identity, Vector3.one);
            avatarInstance.gameObject.SetLayerRecursively(LayerMask.NameToLayer(_layerMask.GetValue()));
            
            ReadyPlayerMeAvatarKinematic kinematic = _avatarInstance.GetKinematic();
            kinematic.SetCharacter(_character);
            kinematic.StartIdle();
            _audio.SetAvatar(_avatarInstance);
            AlterAvatarEventListeners(true);
            
            _onLoadCompleted?.Invoke();
        }

        void OnProgressChanged(ProgressChangeEventArgs args)
        {
            
        }

        void OnFailed(FailureEventArgs args)
        {
            
        }
    }

    private void AlterAvatarEventListeners(bool alter)
    {
        if (_avatarInstance == null) return;
        
        _avatarInstance.onAnimationPhoneCallShowPhone.AlterListener(OnAnimationPhoneCallShowPhone, alter);
        _avatarInstance.onAnimationPhoneCallToggleScreen.AlterListener(OnAnimationPhoneCallToggleScreen, alter);
    }
    
    public void ClearAvatar()
    {
        _audio.ClearAvatar();
        AlterAvatarEventListeners(false);
        
        if (_avatarInstance != null)
        {
            Destroy(_avatarInstance.gameObject);
            _avatarInstance = null;
        }
    }

    

    public void SetAnimatorPropertyMoveSpeed(float value)
    {
        if (_avatarInstance == null) return;
        
        _avatarInstance.GetAnimator().SetFloat(AnimatorPropertyMoveSpeed, value);
        
        if (value > 0.01f)
        {
            CancelEmote(_character.GetClient().IsServer);
        }
    }
    
    private void UpdateAnimatorPropertyEmote()
    {
        _avatarInstance.GetAnimator().SetInteger(AnimatorPropertyEmote, _emoteId);
    }

    public bool ExecuteEmote(SOEmote emote, bool fireEvent, float playTime = -1)
    {
        StopEmoteDependencies();
        
        Debug.Log($"executing emote: {emote.GetKind()}");
        if (emote == null || _avatarInstance == null) return false;

        int emoteId = emote.GetId();
        
        _audio.PlayEmote(emote);
        SetEmoteId(emoteId);
        UpdateAnimatorPropertyEmote();
        _avatarInstance.GetAnimator().SetTrigger(AnimatorPropertyEmoteTrigger);
        
        if(fireEvent) _onEmote.Invoke(emoteId);

        if (playTime > 0)
        {
            StartCoroutine(PlayTimeHandler(emoteId, playTime, _emoteActivityCounter));
            
            IEnumerator PlayTimeHandler(int id, float time, int emoteCounter)
            {
                bool PlayTimeValid() => emoteCounter == _emoteActivityCounter && _emoteId != 0 && _emoteId == id;
                
                while (time > 0f)
                {
                    yield return null;
                    time -= Time.deltaTime;
                    
                    // Emote activity counter has changed, there is no need to cancel it anymore.
                    if (!PlayTimeValid())
                    {
                        Debug.Log("Animation play time handler cancelled.");
                        yield break;
                    }
                }

                if (PlayTimeValid()) CancelEmote(true);
            }
        }

        return true;
    }

    private void SetEmoteId(int value)
    {
        _emoteId = value;
        _emoteActivityCounter++;
    }

    public bool CancelEmote(bool fireEvent)
    {
        if (_emoteId == 0) return false;
        
        SetEmoteId(0);
        StopEmoteDependencies();
        UpdateAnimatorPropertyEmote();
        
        if(fireEvent) _onEmote.Invoke(0);
        return true;
    }

    private void StopEmoteDependencies()
    {
        _audio.StopCurrentEmote();
        SmartphoneDestroy();
    }

    public bool ToggleEmote(SOEmote emote, bool toggle, bool fireEvent, float playTime)
    {
        if (emote == null) return false;
        
        if (toggle)
        {
            return ExecuteEmote(emote, fireEvent, playTime);
        }
        
        // This emote is currently active
        if (_emoteId != 0 && _emoteId == emote.GetId())
        {
            return CancelEmote(fireEvent);
        }
        return false;
    }

    private void OnAnimationPhoneCallShowPhone(bool show)
    {
        if (show)
        {
            if (GetSmartphoneInstance(out Smartphone smartphone))
            {
                smartphone
                    .RandomizeScreenOnColor()
                    .TogglePhoneScreen(true)
                    .PlayAudioIncomingCall();
            }
        }
        else
        {
            SmartphoneDestroy();
        }
    }

    private void OnAnimationPhoneCallToggleScreen(bool isOn)
    {
        if (_smartphone == null) return;
        _smartphone.TogglePhoneScreen(isOn);
    }

    private bool GetSmartphoneInstance(out Smartphone smartphone)
    {
        smartphone = null;
        if (_smartphone == null)
        {
            Transform rightHand = _avatarInstance.GetArmature().GetRightHand();
            if (rightHand != null)
            {
                _smartphone = Instantiate(_prefabs.GetSmartphone(), rightHand, false);
            }
        }
        smartphone = _smartphone;
        return smartphone != null;
    }

    private bool SmartphoneDestroy()
    {
        if (_smartphone == null) return false;
        Destroy(_smartphone.gameObject);
        _smartphone = null;
        return true;
    }

}
