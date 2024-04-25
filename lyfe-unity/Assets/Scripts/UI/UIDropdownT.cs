using System.Collections.Generic;

public abstract class UIDropdownT<T> : UIDropdown where T : UnityEngine.Object
{
    private List<T> _options;

    protected void SetOptions(List<T> value)
    {
        _options = value;
    }
    
    protected void SetOptions(T[] value)
    {
        if (value == null)
        {
            _options = null;
            return;
        }

        SetOptions(new List<T>(value));
    }

    public bool GetValue(out T value)
    {
        value = null;
        if (_options != null)
        {
            value = _options[GetDropdown().value];
        }
        return value != null;
    }
}
