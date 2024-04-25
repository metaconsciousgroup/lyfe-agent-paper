using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;

public abstract class Entity : BaseMonoBehaviour
{
    [SerializeField] private Identifier _identifier;
    [ReadOnly, ShowInInspector] private UserEntity _user;
    
    private bool _isDisposed;
    
    public class MonoEvent : UnityEvent<Entity> { };

    public Identifier GetIdentifier() => _identifier;
    public UserEntity GetUser() => _user;

    public virtual void SetUser(UserEntity value)
    {
        _user = value;
        gameObject.name = _user == null ? "USER_UNDEFINED" : $"{this.GetType().Name} id[{value.Id.GetValue()}] username[{value.Username.GetValue()}]";
    }

    protected abstract void OnDispose();

    public void Dispose()
    {
        if (_isDisposed) return;
        _isDisposed = true;
        OnDispose();
    }
}
