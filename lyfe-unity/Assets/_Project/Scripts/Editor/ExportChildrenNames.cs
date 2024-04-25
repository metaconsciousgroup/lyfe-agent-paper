#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using System.Collections.Generic;
using System.IO;

public class ExportChildrenNames 
{
    [MenuItem("GameObject/Export Children Names to JSON", false, 10)]
    static void ExportChildrenNamesToJSON()
    {
        GameObject obj = Selection.activeGameObject;
        string name = obj.name;

        // Collect the names of all children
        List<string> childrenNames = new List<string>();
        foreach (Transform child in obj.transform)
        {
            if (child.name == "Others")
            {
                continue;
            }
            childrenNames.Add(child.name);
        }

        // Convert to JSON
        string json = JsonUtility.ToJson(new Serialization<string>(childrenNames));

        // Define path and write to a file
        string path = "Assets/Prefabs/World/" + name + "_childrenNames.json";
        File.WriteAllText(path, json);
        
        Debug.Log("Exported children names of " + name + " to " + path);
    }

    [System.Serializable]
    public class Serialization<T>
    {
        [SerializeField]
        List<T> target;
        public List<T> ToList() { return target; }

        public Serialization(List<T> target)
        {
            this.target = target;
        }
    }
}
#endif
