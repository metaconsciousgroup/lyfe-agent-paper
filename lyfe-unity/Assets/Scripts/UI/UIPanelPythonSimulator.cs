using TMPro;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

public class UIPanelPythonSimulator : UIMonoBehaviour
{
    [SerializeField] private Emote _emote;
    [SerializeField] private SummonItem _summonItem;
    [SerializeField] private UnityEvent<SOEmote, bool, float> _onClosestNearByCharacterEmote;
    [SerializeField] private UnityEvent _onSummonAgent;
    [SerializeField] private UnityEvent<SOItem> _onSummonItem;
    [SerializeField] private UnityEvent _allAgentsMoveToRandomLocations;
    [SerializeField] private UnityEvent _stopAllAgentMovement;
    [SerializeField] private UnityEvent _onLookAtSet;
    [SerializeField] private UnityEvent _onLookAtClearForAllClosest;
    
    public void OnButtonRunEmote()
    {
        if (!_emote.dropdown.GetValue(out SOEmote emote))
        {
            Debug.LogWarning("Failed to fetch dropdown.");
            return;
        }
        
        if (!_emote.GetPlayTime(out float playTime))
        {
            Debug.LogWarning("Failed to fetch play time field.");
            return;
        }
        _onClosestNearByCharacterEmote?.Invoke(emote, _emote.toggle.isOn, playTime);
    }

    public void OnButtonSummonAgent()
    {
        _onSummonAgent?.Invoke();
    }
    
    public void OnButtonSummonItem()
    {
        if (!_summonItem.dropdown.GetValue(out SOItem item))
        {
            Debug.LogWarning("Failed to item dropdown.");
            return;
        }
        
        _onSummonItem?.Invoke(item);
    }
    
    public void OnButtonAllAgentsMoveToRandomLocation()
    {
        _allAgentsMoveToRandomLocations?.Invoke();
    }

    public void OnButtonLookAtPlayerClosestAgent()
    {
        _onLookAtSet?.Invoke();
    }
    
    public void OnButtonLookAtClearForAllClosest()
    {
        _onLookAtClearForAllClosest?.Invoke();
    }
    
    public void OnButtonStopAllAgentMovement()
    {
        _stopAllAgentMovement?.Invoke();
    }
    
    [System.Serializable]
    private class Emote
    {
        public UIDropdownSOEmote dropdown;
        public TMP_InputField playTime;
        public Toggle toggle;

        public bool GetPlayTime(out float value)
        {
            value = -1f;
            if (playTime == null) return false;
            string text = playTime.text;
            if (string.IsNullOrEmpty(text)) return true;
            if (!float.TryParse(text, out float parsed)) return false;
            value = parsed;
            return true;
        }
    }

    [System.Serializable]
    private class SummonItem
    {
        public UIDropdownSOItem dropdown;
    }
}
