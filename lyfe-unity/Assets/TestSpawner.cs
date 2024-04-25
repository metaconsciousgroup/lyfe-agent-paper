using System.Collections;
using Lyfe.Creator.v1;
using UnityEngine;

public class TestSpawner : MonoBehaviour
{
    public LyfeCreator_v1_WorldArea area;

    private IEnumerator Start()
    {
        yield break;
        
        /*
        LyfeCreatorWorldArea a = LyfeCreatorWorldArea.AddComponent(area);
        
        while (Application.isPlaying)
        {
            yield return null;
            Transform tr = GameObject.CreatePrimitive(PrimitiveType.Sphere).transform;
            tr.localScale = Vector3.one * 0.1f;
            tr.SetParent(transform, false);

            tr.position = a.GetPoint();
        }
        */
    }
}
