using System.Collections.Generic;
using Sirenix.OdinInspector;
using TMPro;
using UnityEngine;

public abstract class UIDropdown : UIMonoBehaviour
{
    [SerializeField] private TMP_Dropdown _dropdown;

    public TMP_Dropdown GetDropdown() => _dropdown;
    
    protected override void Start()
    {
        base.Start();
        RefreshDropdownOptions();
    }

    [Button]
    public void RefreshDropdownOptions()
    {
        if (OnRefreshDropdownOptions(out List<TMP_Dropdown.OptionData> options))
        {
            _dropdown.options = options;
        }
    }

    protected virtual bool OnRefreshDropdownOptions(out List<TMP_Dropdown.OptionData> options)
    {
        options = null;
        return false;
    }
}
