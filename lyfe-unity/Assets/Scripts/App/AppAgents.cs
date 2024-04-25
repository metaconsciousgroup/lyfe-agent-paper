using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;

public class AppAgents : BaseMonoBehaviour
{
    [SerializeField] private AgentEntity _prefab;

    [SerializeField] private UnityEvent<AgentEntity> _onAgentAdded;
    [SerializeField] private UnityEvent<AgentEntity> _onAgentRemoved;

    public UnityEvent<AgentEntity> onAgentAdded => _onAgentAdded ??= new UnityEvent<AgentEntity>();
    public UnityEvent<AgentEntity> onAgentRemoved => _onAgentRemoved ??= new UnityEvent<AgentEntity>();
    
    public List<AgentEntity> GetAll() => transform.GetComponentsPro<AgentEntity>(GetComponentProExtensions.Scan.Down, 1, 0);

    public AgentEntity Create(CharacterEntity character)
    {
        AgentEntity agentEntity = Instantiate(_prefab);
        Transform tr = agentEntity.transform;
        tr.SetParent(transform, false);
        
        agentEntity.SetCharacter(character);
        agentEntity.onDestroy.AddListener(OnDestroyAgent);
        onAgentAdded.Invoke(agentEntity);
        return agentEntity;
    }

    public bool GetAgentById(string id, out AgentEntity agentEntity)
    {
        agentEntity = null;
        if (!string.IsNullOrEmpty(id))
        {
            foreach (AgentEntity agent in GetAll())
            {
                if(agent.GetCharacter().GetUser().Id.GetValue() != id) continue;
            
                agentEntity = agent;
                break;
            }
        }
        return agentEntity != null;
    }

    private void OnDestroyAgent(BaseMonoBehaviour monoBehaviour)
    {
        // Remove event listener
        monoBehaviour.onDestroy.RemoveListener(OnDestroyAgent);
        
        AgentEntity agentEntity = monoBehaviour.GetComponent<AgentEntity>();
        if (agentEntity == null)
        {
            Debug.LogWarning($"Agent destroy event received but {nameof(AgentEntity)} component does not exist.");
            return;
        }
        onAgentRemoved.Invoke(agentEntity);
    }

    [Button]
    public void AllMoveToRandomLocations()
    {
        foreach (AgentEntity entity in GetAll()) entity.MoveToRandomLocation();
    }

}
