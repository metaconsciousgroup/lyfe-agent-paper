using System;
using Lyfe;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;

public class Player : BaseMonoBehaviour
{
    [ReadOnly, ShowInInspector] private bool _isMoving;
    [ReadOnly, ShowInInspector] private MoveState _moveState = MoveState.Walking;
    [ReadOnly, ShowInInspector] private float _moveSpeed;
    [ReadOnly, ShowInInspector] private CharacterEntity _character;
    [Space]
    [SerializeField] private IdentifierState _stateMouseLook;
    [SerializeField] private IdentifierState _stateMovement;
    [SerializeField] private IdentifierState _stateMouseZoom;
    [Space]
    [SerializeField] private PlayerCamera _camera;
    [SerializeField] private PlayerInput _input;

    [SerializeField] private UnityEvent<CharacterEntity> _onCharacterChanged;
    
    [ReadOnly, ShowInInspector] private bool _cameraOverShoulder = false;
    [ReadOnly, ShowInInspector] private Vector3 _moveDirection2d;
    [ReadOnly, ShowInInspector] private Vector3 _moveDirection;
    
    // TODO these value should be in a SO
    private float _directionSmoothFactor = 10f;
    private float _rotationSmoothFactor = 10f;

    public IdentifierState GetStateMouseLook() => _stateMouseLook;
    public IdentifierState GetStateMovement() => _stateMovement;
    public IdentifierState GetStateMouseZoom() => _stateMouseZoom;

    public bool IsMoving() => _isMoving;
    public PlayerCamera GetCamera() => _camera;
    public PlayerInput GetInput() => _input;

    public bool IsCameraOverShoulder() => _cameraOverShoulder;

    public bool GetCharacter(out CharacterEntity character)
    {
        character = _character;
        return character != null;
    }

    public bool GetUser(out UserEntity user)
    {
        user = null;
        if (_character != null) user = _character.GetUser();
        return user != null;
    }


    private void Update()
    {
        if (!_isMoving || !_stateMovement.IsAllowed())
        {
            StopMoving();
        }

        if (_character == null)
        {
            _moveSpeed = 0f;
        }
        else
        {
            SOCharacter so = _character.GetSO();
            float targetSpeed = _isMoving ? so.GetSpeedByMoveState(_moveState) : 0f;
            bool increasing = _moveSpeed < targetSpeed;
            float velocity = increasing ? so.GetVelocityIncreaseSpeed() : so.GetVelocityDecreaseSpeed();
            _moveSpeed = Mathf.Lerp(_moveSpeed, targetSpeed, Time.deltaTime * velocity);

            // Distance is close enough to clamp
            if (Mathf.Abs(targetSpeed - _moveSpeed) < 0.001f)
            {
                _moveSpeed = targetSpeed;
            }
        }
    }

    private void FixedUpdate()
    {
        FixedUpdateCharacterMovement();
    }

    public void SetCharacter(CharacterEntity value)
    {
        ClearCharacter();
        if (value == null) return;

        _character = value;
        _character.onDestroy.AlterListener(OnCharacterDestroy, true);

        _camera.SetTarget(_character, true);

        // Setup Minimap
        App.Instance.GetUI().GetView<UIViewMinimap>()
            .SetTargetPosition(_character.transform)
            .SetTargetRotation(_character.GetRotation());

        // Set input allowed for mouse look and movement
        GetStateMouseLook().AlterAllow(_character.GetIdentifier(), true);
        GetStateMovement().AlterAllow(_character.GetIdentifier(), true);
        GetStateMouseZoom().AlterAllow(_character.GetIdentifier(), true);

        // Set up gameplay view
        App.Instance.GetUI().GetView<UIViewNearBy>().Set(_character);
        UpdateCharacterNameRenderer();
        _onCharacterChanged.Invoke(_character);
    }

    private void ClearCharacter()
    {
        if (_character == null) return;
        GetStateMouseLook().AlterAllow(_character.GetIdentifier(), false);
        GetStateMovement().AlterAllow(_character.GetIdentifier(), false);
        GetStateMouseZoom().AlterAllow(_character.GetIdentifier(), false);
        App.Instance.GetUI().GetView<UIViewNearBy>().Clear();

        _character.onDestroy.AlterListener(OnCharacterDestroy, false);
        _character = null;
        _onCharacterChanged.Invoke(null);
    }

    private void OnCharacterDestroy(BaseMonoBehaviour monoBehaviour)
    {
        ClearCharacter();
    }

    public void AddCameraRotation(Vector2 delta)
    {
        if (_stateMouseLook.IsAllowed() && !_cameraOverShoulder)
        {
            _camera.AddLook(delta);
        }
    }

    public void AddCameraZoom(float amount)
    {
        if (_stateMouseZoom.IsAllowed() && !_cameraOverShoulder)
        {
            _camera.AddZoom(amount);
        }
    }

    public void CharacterMove(Vector2 direction)
    {
        if (_character == null) return;

        _moveDirection2d = direction;

        if (direction == Vector2.zero || !_stateMovement.IsAllowed())
        {
            StopMoving();
        }
        else
        {
            Internal_SetIsMoving(true);
        }
    }

    public void OnMoveStateChange(MoveState state)
    {
        if (_character == null) return;
        
        Internal_SetMoveState(state);
    }

    private void Internal_SetMoveState(MoveState value)
    {
        if (_moveState == value) return;
        
        //Debug.Log($"Setting move state: {value}");
        _moveState = value;
    }

    private void Internal_SetIsMoving(bool value)
    {
        if (_isMoving == value) return;
        
        //Debug.Log($"Setting is moving: {value}");
        _isMoving = value;
    }

    public void ToggleCameraOverShoulder()
    {
        // Game is not running
        if (!App.Instance.GetGame().IsRunningAndHaveCharacter()) return;
        
        // Something is blocking
        if (IsChatActive() || AnyViewsOpen(
                typeof(UIViewGameMenu),
                typeof(UIViewEmoteSelector),
                typeof(UIViewSettings))
           ) return;
        
        _cameraOverShoulder = !_cameraOverShoulder;
        UpdateCharacterNameRenderer();
        _camera.Clear();
    }

    private void UpdateCharacterNameRenderer()
    {
        if (_character == null) return;
        _character.GetUsernameRenderer().gameObject.SetActive(!_cameraOverShoulder);
    }

    private void StopMoving()
    {
        Internal_SetIsMoving(false);
        _moveDirection2d = Vector3.zero;
    }

    private void FixedUpdateCharacterMovement()
    {
        if (_character == null) return;

        Vector3 targetDirection;
        if (_cameraOverShoulder)
        {
            Vector3 forwardBackwardDirection = _character.GetRotation().forward * _moveDirection2d.y;
            float lateralRotationAngle = _moveDirection2d.x * _rotationSmoothFactor;
            Quaternion lateralRotation = Quaternion.Euler(0, lateralRotationAngle, 0);
            targetDirection = lateralRotation * forwardBackwardDirection;
        }
        else
        {
            targetDirection = GetDirectionNormalized();
        }
        targetDirection.y = 0; // Ensure movement is only on the x-z plane
        _moveDirection = Vector3.Lerp(_moveDirection, targetDirection, Time.fixedDeltaTime * _directionSmoothFactor);

        // Apply the direction to the character's velocity
        _character.GetRigidbody().velocity = _moveDirection.normalized * _moveSpeed;
    }


    private Vector3 GetDirectionNormalized()
    {
        return GetDirectionNormalized(_camera.GetRotationHorizontal(), _moveDirection2d.x, _moveDirection2d.y);
    }

    private Vector3 GetDirectionNormalized(Transform pivot, float leftRight, float forwardBackward)
    {
        Vector3 direction = Vector3.zero;
        direction += pivot.forward * forwardBackward;
        direction += pivot.right * leftRight;
        direction.y = 0f;
        return direction.normalized;
    }

    // Returns true if any of given views are open
    private bool AnyViewsOpen(params Type[] views) => App.Instance.GetUI().AnyOpen(views);

    private bool IsChatActive() => App.Instance.GetUI().GetView<UIViewChat>().IsChatInputFieldFocused;


    public void ClickEscape()
    {
        bool escaped = App.Instance.GetUI().PerformEscape();

        if (escaped) return;
        
        // Game is not running
        if (!App.Instance.GetGame().IsRunning()) return;
        
        // Something is blocking
        if (IsChatActive() || AnyViewsOpen(
                typeof(UIViewGameMenu),
                typeof(UIViewEmoteSelector),
                typeof(UIViewSettings)))
            return;

        // Open game menu
        App.Instance.GetUI().GetView<UIViewGameMenu>().ToggleGroup(true);
    }

    public void OpenEmoteSelector()
    {
        // Game is not running
        if (!App.Instance.GetGame().IsRunningAndHaveCharacter()) return;
        
        // Something is blocking
        if (IsChatActive() || AnyViewsOpen(
                typeof(UIViewGameMenu),
                typeof(UIViewEmoteSelector),
                typeof(UIViewSettings))
            ) return;
                
        App.Instance.GetUI().GetView<UIViewEmoteSelector>().ToggleGroup(true);
    }
    
    public void CloseEmoteSelector()
    {
        if (!App.Instance.GetGame().IsRunningAndHaveCharacter()) return;

        App.Instance.GetUI().GetView<UIViewEmoteSelector>().ToggleGroup(false);
    }
}
