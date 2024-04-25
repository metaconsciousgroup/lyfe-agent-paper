#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

public class SaveAsPrefab 
{
    [MenuItem("GameObject/Save GameObject as Prefab", false, 10)]
    static void SaveGameObjectAsPrefab() // Change this method name
    {
        GameObject obj = Selection.activeGameObject;
        string name = obj.name;
        string address = "Assets/Prefabs/" + name + ".prefab";
        bool result = PrefabUtility.SaveAsPrefabAsset(obj, address);
        if(result)
        {
            Debug.Log("Saved " + name + " as prefab at " + address);
        }
        else
        {
            Debug.LogError("Could not save object as prefab.");
        }
    }
}
#endif
