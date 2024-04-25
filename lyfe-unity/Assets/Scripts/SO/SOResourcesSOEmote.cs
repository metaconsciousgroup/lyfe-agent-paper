using UnityEngine;

[CreateAssetMenu(fileName = "Emotes", menuName = "SO/App/Resources/Emotes", order = 1)]
public class SOResourcesSOEmote : SOResources<SOEmote>
{
    
    public bool GetById(int emoteId, out SOEmote emote)
    {
        emote = null;
        foreach (SOEmote i in GetValues())
        {
            if(i == null) continue;
            if (i.GetId() == emoteId)
            {
                emote = i;
                break;
            }
        }
        return emote != null;
    }
}
