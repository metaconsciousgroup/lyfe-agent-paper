using System.Collections;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Events;

public class CharacterEntity : BaseMonoBehaviour, ICharacterLookDestination
{
    [Header(H_L + "Character" + H_R)]
    [SerializeField] private SOCharacter _sO;
    [SerializeField] private Identifier _identifier;
    [SerializeField] private SOAppSettings _appSettings;

    [ReadOnly, ShowInInspector] private CharacterPermission _permission;

    [SerializeField] private Rigidbody _rigidbody;
    [SerializeField] private NavMeshAgent _navMeshAgent;
    [SerializeField] private CapsuleCollider _capsuleCollider;
    [Space]
    [SerializeField] private UsernameRenderer _usernameRenderer;
    [SerializeField] private ReadyPlayerMeAvatarRenderer _readyPlayerMeAvatarRenderer;
    [SerializeField] private Transform _rotation;
    [SerializeField] private MinimapMarker _minimapMarker;
    [SerializeField] private Transform _chatBubblePivot;
    [SerializeField] private TransformVelocity _velocity;
    [SerializeField] private UserEntity _user;
    [SerializeField] private ClientNetworkBehaviour _client;
    [SerializeField] private NearByCharacters _nearByCharacters;
    [SerializeField] private NearByAreas _nearByAreas;

    [SerializeField] private VisibleCharacters _visibleCharacters;

    [SerializeField] private UnityEvent<CharacterEntity> _onNavMeshAgentMoveEnded;
    [SerializeField] private UnityEvent<ChatMessageData> _onChatMessage;

    [SerializeField] private UnityEvent<AgentMoveData> _onAgentMove;
    
    private bool _isNavMeshAgentMoving;
    [ShowInInspector] private ICharacterLookDestination _lookDestination;

#if UNITY_EDITOR
    [UnityEditor.DrawGizmo(UnityEditor.GizmoType.NotInSelectionHierarchy | UnityEditor.GizmoType.Selected | UnityEditor.GizmoType.InSelectionHierarchy)]
    private static void DrawGizmo(CharacterEntity source, UnityEditor.GizmoType type)
    {
        // Draw look at target
        ICharacterLookDestination dest = source._lookDestination;

        if (dest == null) return;
        if (!dest.GetLookAtDestinationPoint(out Vector3 point)) return;
        
        UnityEditor.Handles.color = Color.green;
        Vector3 offset = Vector3.up * 1.5f;
        UnityEditor.Handles.DrawLine(source.transform.position + offset, point);
    }
#endif

    public SOCharacter GetSO() => _sO;
    public Identifier GetIdentifier() => _identifier;
    public Rigidbody GetRigidbody() => _rigidbody;
    public NavMeshAgent GetNavMeshAgent() => _navMeshAgent;
    public UsernameRenderer GetUsernameRenderer() => _usernameRenderer;
    public ReadyPlayerMeAvatarRenderer GetReadyPlayerMeAvatarRenderer() => _readyPlayerMeAvatarRenderer;
    public Transform GetRotation() => _rotation;
    public MinimapMarker GetMinimapMarker() => _minimapMarker;
    public Transform GetChatBubblePivot() => _chatBubblePivot;
    public NearByCharacters GetNearByCharacters() => _nearByCharacters;
    public NearByAreas GetNearByAreas() => _nearByAreas;
    public TransformVelocity GetVelocity() => _velocity;
    public VisibleCharacters GetVisibleCharacters() => _visibleCharacters;
    public ClientNetworkBehaviour GetClient() => _client;
    public bool IsAgent() => _permission == CharacterPermission.Agent;
    public bool IsPlayer() => _permission == CharacterPermission.Player;
    public UserEntity GetUser() => _user;
    public CharacterPermission GetPermission() => _permission;
    
    private Quaternion _targetRotation = Quaternion.Euler(0f, 0f, 0f);
    public UnityEvent<CharacterEntity> onNavMeshAgentMoveEnded => _onNavMeshAgentMoveEnded ??= new UnityEvent<CharacterEntity>();


    private Vector3 _lastPosition;

    /// <summary>
    /// Returns true if this player character is the player himself.
    /// </summary>
    /// <returns></returns>
    public bool IsMe()
    {
        if (!App.Instance.GetGame().GetPlayer().GetCharacter(out CharacterEntity playerCharacter)) return false;
        return playerCharacter == this;
    }

    public bool IsPlayerButNotMe() => _permission == CharacterPermission.Player && !IsMe();

    protected override void Awake()
    {
        base.Awake();
        _usernameRenderer.SetValue(_user.Username);
        _user.Username.onChanged.AddListener(OnUsernameChanged);
    }

    protected override void Start()
    {
        base.Start();
        Transform tr = transform;
        _lastPosition = tr.position;
        _targetRotation = tr.rotation;
    }

    private void Update()
    {
        UpdateRotation();

        UpdateNavMeshAgent();

        UpdateAnimations();
    }
    
    /**
     * Override.
     */
    public bool GetLookAtDestinationPoint(out Vector3 point) => _readyPlayerMeAvatarRenderer.GetLookAtDestinationPoint(out point);

    private void UpdateAnimations()
    {
        float rawSpeed = _velocity.GetSpeedSmooth();
        float speed = 0f;

        // Produces speed value from 0 (idle) to 1 (walk)
        if (rawSpeed <= _sO.GetWalk())
        {
            float value = Mathf.Clamp(rawSpeed, 0f, _sO.GetWalk());
            speed = Mathf.InverseLerp(0f, _sO.GetWalk(), value);
        }
        // Produces speed value from 1 (walk) to 2 (sprint)
        else
        {
            float value = Mathf.Clamp(rawSpeed, _sO.GetWalk(), _sO.GetSprint());
            speed = 1f + Mathf.InverseLerp(_sO.GetWalk(), _sO.GetSprint(), value);
        }

        // Make sure its from 0 (idle) to 2 (sprint)
        speed = Mathf.Clamp(speed, 0f, _sO.GetSprint());

        _readyPlayerMeAvatarRenderer.SetAnimatorPropertyMoveSpeed(speed);
    }

    public void SetupAsPlayer(bool isMe)
    {
        Setup(CharacterPermission.Player, !isMe, false, isMe, true, !isMe);
    }

    public void SetupAsAgent(bool isServer)
    {
        Setup(CharacterPermission.Agent, isServer, isServer, false, true, true);
    }

    public void SetupAsStatic()
    {
        Setup(CharacterPermission.Undefined, true, false, false, false, false);
    }

    private void Setup(CharacterPermission permission, bool rigidbodyKinematic, bool navMesh, bool colliderEnabled, bool showUsername, bool minimap)
    {
        SetPermission(permission);
        if (rigidbodyKinematic)
        {
            _rigidbody.isKinematic = true;
            _rigidbody.useGravity = false;
            _rigidbody.interpolation = RigidbodyInterpolation.None;
            _rigidbody.collisionDetectionMode = CollisionDetectionMode.Discrete;
        }
        else
        {
            _rigidbody.isKinematic = false;
            _rigidbody.useGravity = true;
            _rigidbody.interpolation = RigidbodyInterpolation.Interpolate;
            _rigidbody.collisionDetectionMode = CollisionDetectionMode.ContinuousSpeculative;
            _rigidbody.MovePosition(transform.position);
            _rigidbody.MoveRotation(transform.rotation);
        }
        _navMeshAgent.enabled = navMesh;
        _capsuleCollider.enabled = true;// colliderEnabled;
        _usernameRenderer.Toggle(showUsername);

        // Minimap
        if (!minimap)
        {
            _minimapMarker.SetVisibleNo();
        }
        else
        {
            SetMinimapMarker(permission);
        }

    }

    private void SetMinimapMarker(CharacterPermission permission)
    {
        _minimapMarker.SetSize(1, 1).SetColor(_appSettings.GetMinimapColor(permission)).SetVisibleYes();
    }

    public void SetPermission(CharacterPermission value)
    {
        _permission = value;
        SetMinimapMarker(value);
    }

    /// <summary>
    /// Add global chat message from agent.
    /// </summary>
    /// <param name="message"></param>
    [Button]
    public void AddChatMessage(string message)
    {
        AddChatMessage(message, App.Instance.GetUI().GetView<UIViewChat>().GetDefaultChannelId());
    }

    /// <summary>
    /// Add global chat message from agent.
    /// </summary>
    /// <param name="message">Chat text message</param>
    /// <param name="channelId">Target chat channel</param>
    [Button]
    public void AddChatMessage(string message, string channelId)
    {
        ChatMessageData chatMessageData = ChatMessageData.From(this, message, channelId);
        BroadcastChatMessage(chatMessageData);
    }

    private void BroadcastChatMessage(ChatMessageData chatMessageData)
    {
        // Validate message.
        if (string.IsNullOrEmpty(chatMessageData.message))
        {
            Debug.LogWarning("Adding chat message with empty text is not allowed, skipping..");
            return;
        }

        // Validate channel id.
        if (string.IsNullOrEmpty(chatMessageData.channelId))
        {
            Debug.LogWarning("Adding chat message with empty channel id is not allowed, skipping..");
            return;
        }
        GetClient().BroadcastChatMessage(chatMessageData);
        _onChatMessage.Invoke(chatMessageData);
    }

    public void AddDirectChatMessage(string message, CharacterEntity receiver)
    {
        HashSet<CharacterEntity> receiverPlayers = new HashSet<CharacterEntity>();
        HashSet<CharacterEntity> receiverAgents = new HashSet<CharacterEntity>();
        if (receiver.GetPermission() == CharacterPermission.Player)
            receiverPlayers.Add(receiver);
        else
            receiverAgents.Add(receiver);

        ChatMessageData chatMessageData = ChatMessageData.From(this, message, ChatMessageData.GetDirectChannelId(this), receiverPlayers, receiverAgents);
        BroadcastChatMessage(chatMessageData);
    }

    public void SetInstantRotation(Quaternion value)
    {
        _rotation.localRotation = _targetRotation = value;
    }

    public void SetInstantRotation(float value)
    {
        switch (_permission)
        {
            case CharacterPermission.Agent:
            {
                if (_lookDestination != null) return;
                break;
            }
        }
        _rotation.rotation = _targetRotation = Quaternion.Euler(0f, value, 0f);
    }

    public float GetBodyColliderHeight()
    {
        return _capsuleCollider.height;
    }

    private void UpdateRotation()
    {
        switch (_permission)
        {
            case CharacterPermission.Agent:
            {
                if (_lookDestination != null)
                {   
                    bool shouldLookAt = true;
                    if (_lookDestination is ClientNetworkBehaviour)
                    {                        
                        CharacterEntity characterEntity = ((ClientNetworkBehaviour) _lookDestination).GetCharacter();
                        shouldLookAt = GetNearByCharacters().GetAllWithPermission(characterEntity.GetPermission()).Contains(characterEntity);
                    }
                    if (_lookDestination.GetLookAtDestinationPoint(out Vector3 point) && shouldLookAt)
                    {
                        Vector3 pos = transform.position;
                        point.y = pos.y;
                        Vector3 direction = (point - pos).normalized;
                
                        Quaternion toRotation = Quaternion.FromToRotation(Vector3.forward, direction);
                        _targetRotation = toRotation;
                        RotateTowardsTarget(0.5f, true);
                    }
                }
                break;
            }
        }
        
        if (_client.IsClient && _lastPosition != transform.position)
        {
            Vector3 curPos = transform.position;
            Vector3 direction = curPos - _lastPosition;
            direction.y = 0f;
            direction.Normalize();
            _lastPosition = curPos;

            if (direction != Vector3.zero)
            {
                Quaternion directionRotation = Quaternion.LookRotation(direction);
                if (IsMe() && App.Instance.GetGame().GetPlayer().IsCameraOverShoulder())
                {
                    float angle = Quaternion.Angle(_rotation.rotation, directionRotation);
                    _targetRotation = angle > 90f && angle < 270 ? Quaternion.LookRotation(directionRotation.Back()) : directionRotation;
                }
                else
                {
                    _targetRotation = directionRotation;
                }
                RotateTowardsTarget(_sO.GetRotationCatchUpSpeed());
            }
        }
    }

    private void RotateTowardsTarget(float speed, bool force = false)
    {
        if (_rotation.rotation != _targetRotation)
        {
            _rotation.rotation = Quaternion.Slerp(_rotation.rotation, _targetRotation, Time.deltaTime * speed);
            if (force) _rigidbody.MoveRotation(_rotation.localRotation);
        }
    }

    private void UpdateNavMeshAgent()
    {
        if (!_navMeshAgent.enabled) return;
        bool isMoving = ResolveNavMeshAgentIsMoving();

        if (_isNavMeshAgentMoving && !isMoving)
        {
            _onNavMeshAgentMoveEnded.Invoke(this);
        }

        _isNavMeshAgentMoving = isMoving;
    }

    private bool ResolveNavMeshAgentIsMoving()
    {
        if (_navMeshAgent == null || !_navMeshAgent.enabled) return false;
        if (!_navMeshAgent.isOnNavMesh) return false;
        if (_navMeshAgent.pathPending) return true;
        if (_navMeshAgent.remainingDistance > _navMeshAgent.stoppingDistance) return true;
        if (_navMeshAgent.hasPath) return true;
        if (_navMeshAgent.velocity.sqrMagnitude == 0f) return false;

        return false;
    }

    [Button]
    public void SetLookAtDestination(ICharacterLookDestination value)
    {
        _lookDestination = value;
    }

    [Button]
    public void ClearLookAtDestination() => _lookDestination = null;

    public bool GetLookAtDestination(out ICharacterLookDestination lookDestination)
    {
        lookDestination = _lookDestination;
        return lookDestination != null;
    }

    public void BroadcastAgentMove(AgentMoveData agentMoveData)
    {
        // Validate message.
        if (string.IsNullOrEmpty(agentMoveData.locationName))
        {
            Debug.LogWarning("Adding agent move with empty location name is not allowed, skipping..");
            return;
        }

        GetClient().BroadcastAgentMove(agentMoveData);
        _onAgentMove.Invoke(agentMoveData);
    }
    private void OnUsernameChanged(string value)
    {
        gameObject.name = $"{GetPermission()} - {value}";
    }


    public bool ExecuteEmote(int emoteId, bool fireEvent)
    {
        if (emoteId == 0)
        {
            return CancelEmote(fireEvent);
        }

        if (!App.Instance.GetConfig().GetEmotes().GetById(emoteId, out SOEmote emote)) return false;
        return ExecuteEmote(emote, fireEvent);
    }

    [Button]
    public bool ExecuteEmote(SOEmote emote, bool fireEvent, float playTime = -1)
    {
        if (_readyPlayerMeAvatarRenderer == null) return false;
        return _readyPlayerMeAvatarRenderer.ExecuteEmote(emote, fireEvent, playTime);
    }

    public bool ToggleEmote(SOEmote emote, bool toggle, bool fireEvent, float playTime)
    {
        
        #if UNITY_STANDALONE_LINUX
            // There is no need to play emotes on Linux.
            StartCoroutine(BroadcastEmoteCoroutine(emote, fireEvent, playTime));
            return true;
        #endif

        #if !UNITY_STANDALONE_LINUX
            if (_readyPlayerMeAvatarRenderer == null) return false;
            return _readyPlayerMeAvatarRenderer.ToggleEmote(emote, toggle, fireEvent, playTime);
        #endif
    }

    private IEnumerator BroadcastEmoteCoroutine(SOEmote emote, bool fireEvent, float playTime)
    {
        if (emote == null) yield break;
        if (!fireEvent) yield break;
        _client.OnAvatarRendererEmote(emote.GetId());
        if (playTime > 0)
        {
            yield return new WaitForSeconds(playTime);
            _client.OnAvatarRendererEmote(0);
        }
    }

    public bool CancelEmote(bool fireEvent)
    {
        if (_readyPlayerMeAvatarRenderer == null) return false;
        return _readyPlayerMeAvatarRenderer.CancelEmote(fireEvent);
    }
}
