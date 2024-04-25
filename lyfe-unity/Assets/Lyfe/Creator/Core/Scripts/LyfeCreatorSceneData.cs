using System.Collections.Generic;
using System.Text;
using Lyfe.Creator.v1;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.SceneManagement;

public class LyfeCreatorSceneData : MonoBehaviour
{
    [ReadOnly, ShowInInspector] private string _sceneName;
    
    // Areas
    [ReadOnly, ShowInInspector] private List<LyfeCreatorWorldArea> _areas = new ();
    [ReadOnly, ShowInInspector] private Dictionary<string, LyfeCreatorWorldArea> _areasMap = new();
    
    // Spawns
    [ReadOnly, ShowInInspector] private List<LyfeCreatorSpawn> _spawns = new ();

    private SOLyfeCreatorSettings _settings;
    
    
    public bool GetAreaByKey(string key, out LyfeCreatorWorldArea entry)
    {
        entry = null;
        foreach (LyfeCreatorWorldArea i in _areas)
        {
            if(i == null) continue;
            if(i.GetKey() != key) continue;
            entry = i;
            break;
        }
        return entry != null;
    }
    
    public bool GetRandomArea(out LyfeCreatorWorldArea area)
    {
        area = null;
        int count = _areas.Count;
        if (count > 0)
        {
            area = count == 1 ? _areas[0] : _areas[Random.Range(0, count)];
        }
        return area != null;
    }

    /// <summary>
    /// Creates new area.
    /// </summary>
    /// <param name="areaData"></param>
    /// <returns></returns>
    private bool AddArea(LyfeCreatorDataWorldArea areaData)
    {
        if (areaData == null) return false;

        string key = areaData.key;

        if (_areasMap.ContainsKey(key))
        {
            Debug.LogWarning($"Area with key '{key}' already exists, skipping..");
            return false;
        }
        
        LyfeCreatorWorldArea area = Instantiate(_settings.GetArea().GetPrefab(), transform).GetComponent<LyfeCreatorWorldArea>();
        area.gameObject.name = $"Area - {key}";
        area.SetData(areaData, _settings);
        area.gameObject.layer = LayerMask.NameToLayer(_settings.GetArea().GetLayerName());
        
        _areas.Add(area);
        _areasMap.Add(key, area);
        return true;
    }


    /// <summary>
    /// Creates new spawn.
    /// </summary>
    /// <param name="spawnData"></param>
    public void AddSpawn(LyfeCreatorDataSpawn spawnData)
    {
        GameObject go = new GameObject($"Spawn");
        go.transform.SetParent(transform, Vector3.zero, Quaternion.identity, Vector3.one);
        LyfeCreatorSpawn spawn = go.AddComponent<LyfeCreatorSpawn>();
        spawn.SetData(spawnData);
        
        _spawns.Add(spawn);
    }

    /// <summary>
    /// Returns random spawn point vector3 from all spawns.
    /// Returns 0,0,0 if no custom spawn points exist.
    /// </summary>
    /// <returns></returns>
    public Vector3 GetRandomSpawnPoint()
    {
        int length = _spawns.Count;
        if(length == 0) return Vector3.zero;
        if (length == 1) return _spawns[0].GetPoint();
        return _spawns[Random.Range(0, length)].GetPoint();
    }
    

    public static bool Create(Scene scene, SOLyfeCreatorSettings settings, out LyfeCreatorSceneData sceneData)
    {
        sceneData = null;
        GameObject[] hierarchy = scene.GetRootGameObjects();
        if (hierarchy == null) return false;

        GameObject sceneDataGo = new GameObject($"Scene Data - {scene.name}");
        sceneData = sceneDataGo.AddComponent<LyfeCreatorSceneData>();
        sceneData._sceneName = scene.name;
        sceneData._settings = settings;

        ProcessV1(hierarchy, sceneData);

        return sceneData != null;
    }
    
    /// <summary>
    /// Processes lyfe creator v1 components.
    /// </summary>
    /// <param name="hierarchy"></param>
    /// <param name="sceneData"></param>
    private static void ProcessV1(GameObject[] hierarchy, LyfeCreatorSceneData sceneData)
    {
        // Areas
        foreach (LyfeCreator_v1_WorldArea i in hierarchy.GetComponentsPro<LyfeCreator_v1_WorldArea>(GetComponentProExtensions.Scan.Down, 0, -1))
            sceneData.AddArea(LyfeCreatorDataWorldArea.Resolve(i));
        
        // Spawns
        foreach (LyfeCreator_v1_Spawn i in hierarchy.GetComponentsPro<LyfeCreator_v1_Spawn>(GetComponentProExtensions.Scan.Down, 0, -1))
            sceneData.AddSpawn(LyfeCreatorDataSpawn.Resolve(i));
    }
    
    public override string ToString()
    {
        StringBuilder sb = new StringBuilder();
        sb.AppendLine($"{nameof(LyfeCreatorSceneData)}");
        sb.AppendLine($"\tName: {this._sceneName}");
        sb.AppendLine($"\tAreas:");
        foreach (LyfeCreatorWorldArea area in _areas)
        {
            sb.AppendLine($"\t\t{area.GetKey()}");
        }
        return sb.ToString();
    }
}
