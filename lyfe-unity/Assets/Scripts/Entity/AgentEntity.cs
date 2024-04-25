using System.Collections;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;

public class AgentEntity : BaseMonoBehaviour
{
    [Header("Entity - Agent")]
    [SerializeField] private MoveState _moveState = MoveState.Walking;
    [ReadOnly, ShowInInspector] private CharacterEntity _character;

    [SerializeField] private UnityEvent<AgentEntity, NavigationPoint> _onCharacterNavMeshAgentMoveEnded;
    
    
    public UnityEvent<AgentEntity, NavigationPoint> onCharacterNavMeshAgentMoveEnded => _onCharacterNavMeshAgentMoveEnded ??= new UnityEvent<AgentEntity, NavigationPoint>();
    public CharacterEntity GetCharacter() => _character;

    private NavigationPoint _currentDestination;

    private InDataAgent _data;
    private IEnumerator _dynamicMoveHandler;
    

    protected override void OnDestroy()
    {
        base.OnDestroy();
        ClearCharacter();
    }

    public void SetData(InDataAgent value)
    {
        _data = value;
        // // Behavior name is used to identify agent in python
        //  _behaviorParameters.BehaviorName = value.user.id;
         
         InDataUser userData = _data.user;
         ClientNetworkBehaviour client = GetCharacter().GetClient();
        
         client.SetSyncId(userData.id);
         client.FromServer_SetPermission(CharacterPermission.Agent);
         client.FromServer_SetUsername(userData.username);
         client.FromServer_SetCharacterModelPath(_data.character.modelPath);
    }

    [Button]
    public void SetMoveState(MoveState value)
    {
        _moveState = value;
        UpdateCharacterMaxMoveSpeed();
    }

    private void UpdateCharacterMaxMoveSpeed()
    {
        if (_character == null) return;
        _character.GetNavMeshAgent().speed = _character.GetSO().GetSpeedByMoveState(_moveState);
    }

    public void SetCharacter(CharacterEntity value)
    {
        // Clear previous character
        ClearCharacter();
        
        _character = value;
        UpdateCharacterMaxMoveSpeed();
        AlterCharacterEvents(true);
    }

    private void ClearCharacter()
    {
        AlterCharacterEvents(false);
        _character = null;
    }

    private void AlterCharacterEvents(bool alter)
    {
        if (_character == null) return;
        _character.onNavMeshAgentMoveEnded.AlterListener(OnCharacterNavMeshAgentMoveEnded, alter);
        _character.onDestroy.AlterListener(OnCharacterDestroy, alter);
    }

    private void OnCharacterDestroy(BaseMonoBehaviour monoBehaviour)
    {
        AlterCharacterEvents(false);
        Destroy(gameObject);
    }

    public void SetMoveDestination(NavigationPoint value)
    {
        _currentDestination = value;
        if (_currentDestination == null) return;
        if (!_currentDestination.IsValid()) return;

        _character.GetNavMeshAgent().isStopped = false;
        _character.GetNavMeshAgent().stoppingDistance = _currentDestination.GetStoppingDistance();
        _character.GetNavMeshAgent().SetDestination(_currentDestination.GetPoint());

        if (_currentDestination.IsPointDynamic())
        {
            if (_dynamicMoveHandler == null)
            {
                _dynamicMoveHandler = DynamicMoveDestinationHandler();
                StartCoroutine(_dynamicMoveHandler);
            }
        }
    }

    public void StopMove()
    {
        if(_dynamicMoveHandler != null) StopCoroutine(_dynamicMoveHandler);
        _dynamicMoveHandler = null;
        _currentDestination = null;
        _character.GetNavMeshAgent().isStopped = true;
    }

    private IEnumerator DynamicMoveDestinationHandler()
    {
        YieldInstruction waitTime = new WaitForSeconds(0.3f);
        
        while (_dynamicMoveHandler != null && _currentDestination != null && _currentDestination.IsPointDynamic())
        {
            yield return waitTime;
            _character.GetNavMeshAgent().SetDestination(_currentDestination.GetPoint());
        }
        _dynamicMoveHandler = null;
    }

    /// <summary>
    /// Moves agent character to random level destination.
    /// </summary>
    [Button]
    public void MoveToRandomLocation()
    {
        if (!App.Instance.GetGame().GetCurrentLevel(out LyfeCreatorSceneData currentLevel)) return;
        if (!currentLevel.GetRandomArea(out LyfeCreatorWorldArea area)) return;

        NavigationPointWorld navigationPoint = NavigationPointWorld.From(area);
        SetMoveDestination(navigationPoint);
    }
    
    [Button]
    public void TestFollowPlayer()
    {
        if (!App.Instance.GetGame().GetPlayer().GetCharacter(out CharacterEntity playerCharacter)) return;

        NavigationPointCharacter navigationPoint = NavigationPointCharacter.From(playerCharacter);
        SetMoveDestination(navigationPoint);
    }

    private void OnCharacterNavMeshAgentMoveEnded(CharacterEntity character)
    {
        onCharacterNavMeshAgentMoveEnded.Invoke(this, _currentDestination);
    }
}