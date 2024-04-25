using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using System.IO;
using SimpleJSON;


public class ItemGenerator : MonoBehaviour
{
    private string geoJSONFilePath = "WorldMap/item_layout";

    private JSONNode geoJSONData;

    private void GenerateItems()
    {
        if (geoJSONData == null) return;

        foreach (JSONNode feature in geoJSONData["features"])
        {
            string featureType = feature["properties"]["feature_type"];
            if (featureType == "item")
            {
                GenerateItem(feature["geometry"]["coordinates"].AsArray, feature["properties"]["name"], 
                 feature["properties"]["display_name"], feature["properties"]["prefab_path"]);
            }
        }
    }

    private void GenerateItem(JSONArray itemCoordinates, string itemName, string displayName, string prefabPath)
    {
        // Get the first 2 coordinates, which are the x and z coordinates of the agent
        float x = itemCoordinates[0].AsFloat;
        float z = itemCoordinates[1].AsFloat;
        Vector3 center = new Vector3(x, 0.0f, z);

        
        // Load agent from the special Resources folder
        // This is the general base agent. It's part will be replaced
        GameObject itemPrefab = Resources.Load<GameObject>(prefabPath);
        if (itemPrefab != null)
        {
            // Instantiate the agent
            GameObject item = Instantiate(itemPrefab, center, Quaternion.identity);
            item.name = itemName;
            item.tag = "item";

            // Calculate the size of the agent
            float width = item.GetComponent<Transform>().localScale.x;
            float length = item.GetComponent<Transform>().localScale.z;
            float height = item.GetComponent<Transform>().localScale.y;


            Vector3 currentSize = item.GetComponent<Renderer>().bounds.size;
            item.transform.position = center + new Vector3(0.0f, 0.5f, 0.0f);

            // Add BoxCollider component
            BoxCollider boxCollider = item.AddComponent<BoxCollider>();
            boxCollider.size = new Vector3(width, height, length) * 1.2f;
            boxCollider.center = new Vector3(0, height/2.0f, 0); 
            boxCollider.isTrigger = true;

            // Add TextMeshPro component for displaying the agent's name
            GameObject textObj = new GameObject("ItemNameText");
            textObj.transform.SetParent(item.transform);
            TextMeshPro textMeshPro = textObj.AddComponent<TextMeshPro>();
            textMeshPro.text = displayName;
            textMeshPro.fontSize = 5;
            textMeshPro.color = Color.black;
            textMeshPro.alignment = TextAlignmentOptions.Center;

            textObj.transform.localPosition = new Vector3(0, height * 1.1f, 0);
            textObj.transform.Rotate(0, 180, 0, Space.Self);

        }
        else
        {
            Debug.LogError("Prefab not found for itemPrefab");
        }
    }


    private void LoadGeoJSON()
    {
        // Note: IMPORTANT!
        // After building .app, the sources can only be inside Resources/ folder
        // .json and .geojson are not supported
        TextAsset jsonData = Resources.Load<TextAsset>(geoJSONFilePath);
        string geoJSONText = jsonData.text;

        geoJSONData = JSON.Parse(geoJSONText);
    }

    // Start is called before the first frame update
    void Start()
    {
        LoadGeoJSON();
        GenerateItems();
    }


    // Update is called once per frame
    void Update()
    {
        
    }
}
