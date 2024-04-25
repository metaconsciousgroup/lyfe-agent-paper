using System;
using TMPro;
using UnityEngine;

public class UsernameRenderer : BaseMonoBehaviour
{
    [SerializeField] private Identifier _identifier;
    [SerializeField] private Transform _pivot;
    [SerializeField] private TMP_Text _tmp;
    [SerializeField] private MeshRenderer _meshRenderer;

    
    private ValueString _username;

    public Identifier GetIdentifier() => _identifier;

    public void SetValue(ValueString value)
    {
        if (_username != null)
        {
            _username.onChanged.RemoveListener(OnUsernameChanged);
            _username = null;
        }

        _username = value;
        if (_username != null)
        {
            _tmp.SetText(_username.GetValue());
            _meshRenderer.enabled = true;
            _username.onChanged.AddListener(OnUsernameChanged);
        }
        else
        {
            _tmp.Clear();
        }
    }

    private void OnUsernameChanged(string value)
    {
        _tmp.SetText(value);
        _meshRenderer.enabled = true;
    }

    public void Clear()
    {
        _tmp.Clear();
    }

    public void Toggle(bool show)
    {
        gameObject.SetActive(show);
    }

    public string GetUsername()
    {
        return _username.GetValue();
    }
}
