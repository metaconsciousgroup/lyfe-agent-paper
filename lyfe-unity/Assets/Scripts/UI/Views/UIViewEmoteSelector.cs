using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class UIViewEmoteSelector : UIView
{
    protected override void OnGroupOpened()
    {
       
    }

    protected override void OnGroupClosed()
    {
        
    }


    public bool SelectEmote(SOEmote emote)
    {
        if (emote == null) return false;
        Debug.Log($"{GetType().Name} selected emote {emote.GetKey()}");

        if (!App.Instance.GetGame().GetPlayer().GetCharacter(out CharacterEntity character))
        {
            Debug.LogWarning($"{GetType().Name} failed to execute emote {emote.GetKey()} player character does not exist.");
            return false;
        }

        bool success = character.ExecuteEmote(emote, true);

        if (!success)
        {
            Debug.LogWarning($"{GetType().Name} failed to execute emote {emote.GetKey()}");
        }
        return success;
    }
}
