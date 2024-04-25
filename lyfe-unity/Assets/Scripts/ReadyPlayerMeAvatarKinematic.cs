using System.Collections;
using Sirenix.OdinInspector;
using UnityEngine;

public class ReadyPlayerMeAvatarKinematic : BaseMonoBehaviour
{
    [ReadOnly, SerializeField] private ReadyPlayerMeAvatar _avatar;
    [ReadOnly, SerializeField] private ReadyPlayerMeAvatar.Armature _armature;
    [ReadOnly, SerializeField] private SOReadyPlayerMeAvatarSettings _settings;
    [ReadOnly, SerializeField] private CharacterEntity _character;
    
    [ReadOnly, ShowInInspector] private Vector3 _eyeRotationCurrent;
    [ReadOnly, ShowInInspector] private Vector3 _eyeRotationTarget;
    [Range(-1f, 1f)]
    [SerializeField] private float _rotHeadVert = 0f;

    private IEnumerator _eyesIdleHandler = null;

    [Title("IK Weights")]
    [ReadOnly, ShowInInspector, Range(0f, 1f)] private float _lookAtHeadWeight;
    [ReadOnly, ShowInInspector, Range(0f, 1f)] private float _lookAtHeadWeightTarget;
    
    public void Initialize(ReadyPlayerMeAvatar avatar)
    {
        _avatar = avatar;
        _armature = avatar.GetArmature();
        _settings = _avatar.GetSO();
    }
    
    public void SetCharacter(CharacterEntity value) => _character = value;

    
    private void Update()
    {
        UpdateLookAt();
    }

    private void UpdateLookAt()
    {
        _lookAtHeadWeightTarget = 0f;

        if (_settings != null)
        {
            if (GetLookAtDestination(out Vector3 point))
            {
                _lookAtHeadWeightTarget = _settings.GetLookAtWeight();
            }
        }
        
        _lookAtHeadWeight = Mathf.Lerp(_lookAtHeadWeight, _lookAtHeadWeightTarget, Time.smoothDeltaTime * 2f);
    }
    
    private void LateUpdate()
    {
        //UpdateCustomHeadLook();
    }

    private void OnAnimatorIK(int layerIndex)
    {
        if (_avatar != null && _settings != null)
        {
            Animator animator = _avatar.GetAnimator();
            if (animator != null)
            {
                GetLookAtDestination(out Vector3 point);

                if (point != Vector3.zero)
                {
                    animator.SetLookAtWeight(_settings.GetWeight(), _settings.GetBodyWeight(), _lookAtHeadWeight, _settings.GetEyesWeight(), _settings.GetClampWeight());
                    animator.SetLookAtPosition(point);
                    //animator.SetIKRotationWeight(_kRotationWeight);
                }
            }
        }
    }

    [Button]
    public void StartIdle()
    {
        Eyes();

        void Eyes()
        {
            // Already started
            if (_eyesIdleHandler != null) return;
            // Start
            _eyesIdleHandler = EyeMover();
            StartCoroutine(_eyesIdleHandler);
        }
    }

    [Button]
    public void StopIdle()
    {
        Eyes();

        void Eyes()
        {
            // Already stopped.
            if (_eyesIdleHandler == null) return;
            // Stop
            StopCoroutine(_eyesIdleHandler);
            _eyesIdleHandler = null;
            _eyeRotationTarget = Vector3.zero;
        }
    }

    private IEnumerator EyeMover()
    {
        while (IsPlaying())
        {
            yield return new WaitForSeconds(_settings.GetEyeIdleTargetDelay().GetRandomInRange());
            
            _eyeRotationTarget.x = _settings.GetEyeIdleVertical().GetRandomInRange();
            _eyeRotationTarget.y = _settings.GetEyeIdleHorizontal().GetRandomInRange();
        }
        
        _eyesIdleHandler = null;
    }

    private bool GetLookAtDestination(out Vector3 point)
    {
        point = Vector3.zero;
        if (_character == null) return false;
        if(!_character.GetLookAtDestination(out ICharacterLookDestination lookDestination)) return false;
        return lookDestination.GetLookAtDestinationPoint(out point);
    }

    

    private void UpdateCustomHeadLook()
    {
        // Update eye movement
        _eyeRotationCurrent = Vector3.Lerp(_eyeRotationCurrent, _eyeRotationTarget, Time.smoothDeltaTime * _settings.GetEyeIdleTargetFollowSpeed());

        if(_armature.GetEyeLeft() != null) _armature.GetEyeLeft().localEulerAngles = _eyeRotationCurrent;
        if(_armature.GetEyeRight() != null) _armature.GetEyeRight().localEulerAngles = _eyeRotationCurrent;

        float neckApply = _settings.GetNeckRotationImpact();
        
        UnityDataMinMaxFloat horRange = _settings.GetHeadRotationHorizontal();
        float t = (_rotHeadVert + 1f) * 0.5f; // convert from (-1, 1) to (0, 1) 
        float headHorizontalRotation = Mathf.Lerp(horRange.GetMin(), horRange.GetMax(), t);

        // Update neck rotation
        if (_armature.GetNeck() != null)
        {
            Vector3 n = _settings.GetNeckRotationInitial();
            n.y += headHorizontalRotation * neckApply;
            _armature.GetNeck().localEulerAngles = n;
        }

        // Update head rotation
        if (_armature.GetHead() != null)
        {
            Vector3 n = _settings.GetHeadRotationInitial();
            n.y += headHorizontalRotation * (1f - neckApply);
            _armature.GetHead().localEulerAngles = n;
        }
    }
}
