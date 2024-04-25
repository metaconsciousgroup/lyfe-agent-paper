using UnityEngine;

public class AgentBase : BaseMonoBehaviour
{
    [SerializeField] private CharacterEntity _character;
    [SerializeField] private UsernameRenderer _usernameRenderer;

    public CharacterEntity GetCharacter() => _character;
    public UsernameRenderer GetUsernameRenderer() => _usernameRenderer;

    public void SetCharacter(CharacterEntity value)
    {
        if (_character != null)
        {
            Destroy(_character.gameObject);
            _character = null;
        }
        
        _character = value;
        if (_character != null)
        {
            _character.transform.SetParent(transform, Vector3.zero, Quaternion.identity, Vector3.one);
        }
    }
}