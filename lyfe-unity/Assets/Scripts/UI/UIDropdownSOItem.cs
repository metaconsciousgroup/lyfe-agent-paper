using System.Collections.Generic;
using System.Linq;
using TMPro;
using UnityEngine;

public class UIDropdownSOItem : UIDropdownT<SOItem>
{
    [SerializeField] private SOResourcesSOItem _items;

    protected override bool OnRefreshDropdownOptions(out List<TMP_Dropdown.OptionData> options)
    {
        SOItem[] items = _items.GetValues();
        SetOptions(items);
        options = items.Select(i => new TMP_Dropdown.OptionData(i.GetTitle())).ToList();
        return true;
    }
}
