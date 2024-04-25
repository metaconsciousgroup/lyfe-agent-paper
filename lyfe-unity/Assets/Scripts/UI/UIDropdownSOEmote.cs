using System.Collections.Generic;
using System.Linq;
using TMPro;
using UnityEngine;

public class UIDropdownSOEmote : UIDropdownT<SOEmote>
{
    [SerializeField] private SOResourcesSOEmote _emotes;

    protected override bool OnRefreshDropdownOptions(out List<TMP_Dropdown.OptionData> options)
    {
        SOEmote[] emotes = _emotes.GetValues();
        SetOptions(emotes);
        options = emotes.Select(i => new TMP_Dropdown.OptionData(i.GetKind().ToString())).ToList();
        return true;
    }
}
