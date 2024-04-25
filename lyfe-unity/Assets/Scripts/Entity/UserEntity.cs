using UnityEngine;

public class UserEntity : BaseMonoBehaviour
{
    [Space]
    [SerializeField] private ValueString _id;
    [SerializeField] private ValueString _username;

    public ValueString Id => _id;
    public ValueString Username => _username;

    public void OnIdValueChanged(string value)
    {
        UpdateGameObjectName();
    }

    public void OnUsernameValueChanged(string value)
    {
        UpdateGameObjectName();
    }
    

    private void UpdateGameObjectName()
    {
        gameObject.name = $"{nameof(UserEntity)} id[{_id.GetValue().ToStringNullable()}] username[{_username.GetValue().ToStringNullable()}]";
    }

    public void Dispose()
    {
        Destroy(gameObject);
    }
}