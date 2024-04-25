using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.InputSystem;

public class PlayerInput : BaseMonoBehaviour
{
    [SerializeField] private KeyCode _keyCodeEmoteSelector = KeyCode.V;
    
    private PlayerInputActions _inputActions;
    
    [ReadOnly, ShowInInspector] private Vector2 _move;
    [ReadOnly, ShowInInspector] private Vector2 _lookNormalized;

    [SerializeField] private UnityEvent<Vector2> _onMoveChanged;
        
    [SerializeField] private UnityEvent<MoveState> _onMoveStateChanged;

    [SerializeField] private UnityEvent<Vector2> _onLookChanged;
    [SerializeField] private UnityEvent<float> _onZoomChanged;
    [SerializeField] private UnityEvent _onChatFocus;
    [SerializeField] private UnityEvent _onChatUnfocus;
    [SerializeField] private UnityEvent _onEscape;
    [SerializeField] private UnityEvent _onTab;
    
    [SerializeField] private UnityEvent _onEmoteSelectorOpen;
    [SerializeField] private UnityEvent _onEmoteSelectorClose;

    private bool _isRightMouseButtonDown;
    
    public Vector2 GetMoveDirection() => _move;
    

    protected override void Awake()
    {
        base.Awake();
        _inputActions = new PlayerInputActions();

        _inputActions.Player.Move.performed += OnMovePerformed;
        _inputActions.Player.Move.canceled += OnMoveCanceled;
        
        _inputActions.Player.Look.performed += OnLookPerformed;

        _inputActions.Player.Zoom.performed += OnZoomPerformed;

        _inputActions.Player.FocusChat.performed += OnFocusChatPerformed;
        //_inputActions.Player.UnfocusChat.performed += OnUnfocusChatPerformed;
    }

    private void Update()
    {
        _isRightMouseButtonDown = Input.GetKey(KeyCode.Mouse1);

        if (Input.GetKeyDown(KeyCode.Escape))
        {
            _onEscape.Invoke();
        }

        if (Input.GetKeyDown(KeyCode.LeftShift))
        {
            _onMoveStateChanged?.Invoke(MoveState.Sprinting); // Trigger event for Sprinting
        }
        else if (Input.GetKeyUp(KeyCode.LeftShift))
        {
            _onMoveStateChanged?.Invoke(MoveState.Walking); // Trigger event for Walking
        }

        if (Input.GetKeyDown(KeyCode.Tab))
        {
            _onTab.Invoke();
        }

        // UI View emote selector
        if (Input.GetKeyDown(_keyCodeEmoteSelector))
        {
            _onEmoteSelectorOpen?.Invoke();
        }
        
        else if (Input.GetKeyUp(_keyCodeEmoteSelector))
        {
            _onEmoteSelectorClose?.Invoke();
        }
    }

    protected override void OnEnable()
    {
        base.OnEnable();
        _inputActions.Enable();
    }

    protected override void OnDisable()
    {
        base.OnDisable();
        _inputActions.Disable();
    }

    private void OnMovePerformed(InputAction.CallbackContext context)
    {
        Vector2 value = context.ReadValue<Vector2>();
        SetMove(value);
    }

    private void OnMoveCanceled(InputAction.CallbackContext context)
    {
        SetMove(Vector2.zero);
    }
    
    private void OnLookPerformed(InputAction.CallbackContext context)
    {
        if (_isRightMouseButtonDown)
        {
            Vector2 value = context.ReadValue<Vector2>();
            SetLook(value);
        }
    }

    private void OnZoomPerformed(InputAction.CallbackContext context)
    {
        float value = context.ReadValue<float>();
        value *= 0.01f;
        _onZoomChanged.Invoke(value);
    }

    private void SetMove(Vector2 value)
    {
        _move = value;
        _onMoveChanged.Invoke(value);
    }

    private void SetLook(Vector2 value)
    {
        value.x /= Screen.height;
        value.y /= Screen.height;
        _lookNormalized = value;
        _onLookChanged.Invoke(value);
    }

    private void OnFocusChatPerformed(InputAction.CallbackContext context)
    {
        _onChatFocus?.Invoke();
    }
    
    private void OnUnfocusChatPerformed(InputAction.CallbackContext context)
    {
        _onChatUnfocus?.Invoke();
    }
}
