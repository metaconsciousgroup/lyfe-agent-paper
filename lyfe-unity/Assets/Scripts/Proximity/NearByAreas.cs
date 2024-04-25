using UnityEngine;

public class NearByAreas : NearBy<LyfeCreatorWorldArea>
{
    [SerializeField] private bool _debug;
    
    protected override bool OnEnterCheck(GameObject other, out LyfeCreatorWorldArea target)
    {
        target = other.GetComponent<LyfeCreatorWorldArea>();
        return target != null;
    }

    protected override bool OnExitCheck(GameObject other, out LyfeCreatorWorldArea target)
    {
        target = other.GetComponent<LyfeCreatorWorldArea>();
        return target != null;
    }

    protected override void OnEntered(LyfeCreatorWorldArea target)
    {
        if(_debug)
            Debug.Log($"Entered area '{target.GetKey()}'");
    }

    protected override void OnExited(LyfeCreatorWorldArea target)
    {
        if(_debug)
            Debug.Log($"Exited area '{target.GetKey()}'");
    }

}
