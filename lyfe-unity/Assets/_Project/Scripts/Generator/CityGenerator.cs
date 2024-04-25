using UnityEngine;
using TMPro;
using SimpleJSON;

// 1. NavMeshSurface is not working

/*
Running this code will generate a City game object.
The city game object will have the following children:
    - Ground
    - Buildings
    - Streets
You can save the city as a prefab and instantiate it in other scenes
by right clicking on the city game object in the hierarchy and selecting "Save as prefab".
*/


public class CityGenerator : MonoBehaviour
{
    private string geoJSONFilePath = "WorldMap/smallville_layout";
    private GameObject city;
    private GameObject streets;
    private GameObject buildings;

    private float worldWidth = 100.0f;
    private float worldLength = 100.0f;

    // Start is called before the first frame update
    void Start()
    {
        GenerateCity(geoJSONFilePath);
        Debug.Log("City generated!");
    }

    private void GenerateCity(string geoJSONFilePath)
    {
        city = new GameObject("City");
        buildings = new GameObject("Buildings");
        buildings.transform.parent = city.transform;
        streets = new GameObject("Streets");
        streets.transform.parent = city.transform;
        

        JSONNode geoJSONData = LoadGeoJSON(geoJSONFilePath);
        // Early exit if no data
        if (geoJSONData == null) return;

        // Generate city elements
        foreach (JSONNode feature in geoJSONData["features"])
        {
            string featureType = feature["properties"]["feature_type"];
            if (feature["properties"]["feature_type"] == "ground")
            {
                GenerateGround(feature["geometry"]["coordinates"].AsArray);
            }
            else if (featureType == "building")
            {
                GenerateBuilding(feature["geometry"]["coordinates"].AsArray, feature["properties"]["name"], feature["properties"]["prefab_path"]);
            }
            else if (featureType == "street")
            {
                GenerateStreet(feature["geometry"]["coordinates"].AsArray);
            }
        }

        // // After generating the city, bake the NavMeshes
        // foreach (NavMeshSurface surface in FindObjectsOfType<NavMeshSurface>())
        // {
        //     surface.BuildNavMesh();
        // }

        Debug.Assert(worldWidth > 0f && worldLength > 0f, "World dimensions are not set correctly.");
    }

    private void GenerateGround(JSONArray groundCoordinates) 
    {
        Vector3[] corners = GetCornersFromCoordinates(groundCoordinates);
        Vector3 center = CalculateCenter(corners);
        float width = Vector3.Distance(corners[0], corners[1]);
        float length = Vector3.Distance(corners[1], corners[2]);
        const float height = 1f;

        // Update the world's size
        worldWidth = width;
        worldLength = length;
        
        // Load and instantiate the ground prefab at the center position
        GameObject groundPrefab = Resources.Load<GameObject>("Prefabs/Ground");
        GameObject ground = Instantiate(groundPrefab, center, Quaternion.identity);
        ground.name = "ground";
        
        // Adjust the ground's scale and position
        ground.transform.localScale = new Vector3(width, height, length);
        ground.transform.position = center - new Vector3(0.0f, height / 2, 0.0f); // Position it at bottom-middle

        ground.transform.parent = city.transform;

        // // After instantiating the ground, add a NavMeshSurface component to it
        // NavMeshSurface navMeshSurface = ground.GetComponent<NavMeshSurface>();
        // navMeshSurface.collectObjects = CollectObjects.Children;  // Only consider this object's children when baking the NavMesh
    }
    
    private void GenerateBuilding(JSONArray buildingCoordinates, string buildingName, string prefabPath)
    {
        Vector3[] corners = GetCornersFromCoordinates(buildingCoordinates);        
        Vector3 center = CalculateCenter(corners);
        float width = Vector3.Distance(corners[0], corners[1]);
        float length = Vector3.Distance(corners[1], corners[2]);
        float height = Mathf.Max(width, length) * 1.5f;
        
        // Instantiate the building
        GameObject buildingPrefab = Resources.Load<GameObject>(prefabPath);
        if (buildingPrefab == null)
        {
            Debug.LogError("Prefab not found at path: " + prefabPath);
        }
        // Instantiate the building
        GameObject building = Instantiate(buildingPrefab, center, Quaternion.identity);
        building.name = buildingName;
        building.tag = "building";
        building.transform.parent = buildings.transform;

        // Calculate the scale factors
        Vector3 currentSize = building.GetComponent<Renderer>().bounds.size;
        Vector3 scaleFactor = new Vector3(width / currentSize.x, height / currentSize.y, length / currentSize.z);
        building.transform.localScale = scaleFactor;
        building.transform.position = center + new Vector3(0.0f, scaleFactor.y/50.0f, 0.0f);

        // Add BoxCollider component
        BoxCollider boxCollider = building.AddComponent<BoxCollider>();
        boxCollider.size = new Vector3(2.0f, 2.0f, 2.0f);
        boxCollider.center = new Vector3(0, 1.0f, 0); // Since the height is 2.0f, the center in y direction should be 1.0f to align with the building's center
        boxCollider.isTrigger = true;

        // Add TextMeshPro component for displaying the building's name
        GameObject textObj = new GameObject("BuildingNameText");
        textObj.transform.SetParent(building.transform);
        TextMeshPro textMeshPro = textObj.AddComponent<TextMeshPro>();
        textMeshPro.text = buildingName;
        textMeshPro.fontSize = 15;
        textMeshPro.color = Color.black;
        textMeshPro.alignment = TextAlignmentOptions.Center;

        textObj.transform.localPosition = new Vector3(0, currentSize.y * 1.1f + textMeshPro.bounds.size.y, 0);
    }

    private void GenerateStreet(JSONArray streetCoordinates)
    {
        Vector3[] corners = GetCornersFromCoordinates(streetCoordinates);
        Vector3 center = CalculateCenter(corners);
        float width = Vector3.Distance(corners[0], corners[1]);
        float length = Vector3.Distance(corners[1], corners[2]);

        if (corners[0].x == corners[1].x) {
            float temp = width;
            width = length;
            length = temp;
        }
        
        // TODO: Probably better way to generate street
        GameObject streetPrefab = Resources.Load<GameObject>("Prefabs/Street");
        GameObject street = Instantiate(streetPrefab, center, Quaternion.identity);
        street.name = "street";
        // Calculate the scale factors
        Vector3 currentSize = street.GetComponent<Renderer>().bounds.size;
        float height = 0.1f;
        Vector3 scaleFactor = new Vector3(width / currentSize.x, height / currentSize.y, length / currentSize.z);
        street.transform.localScale = new Vector3(width, height, length);
        street.transform.position = center;
        street.transform.parent = streets.transform;

        // NavMeshSurface navMeshSurface = street.GetComponent<NavMeshSurface>();
        // Debug.Log(navMeshSurface);
        // navMeshSurface.collectObjects = CollectObjects.Children;  // Only consider this object's children when baking the NavMesh
    }

    private Vector3[] GetCornersFromCoordinates(JSONArray coordinates)
    {
        coordinates = coordinates[0].AsArray;

        Vector3[] corners = new Vector3[4];
        for (int i = 0; i < 4; i++)
        {
            float x = coordinates[i][0].AsFloat;
            float z = coordinates[i][1].AsFloat;
            corners[i] = new Vector3(x, 0.0f, z);
        }

        return corners;
    }


    private Vector3 CalculateCenter(Vector3[] corners)
    {
        Vector3 center = Vector3.zero;
        foreach (Vector3 corner in corners)
        {
            center += corner;
        }
        center /= corners.Length;
        return center;
    }


    private JSONNode LoadGeoJSON(string geoJSONFilePath)
    {
        // Note: IMPORTANT!
        // After building .app, the sources can only be inside Resources/ folder
        // .json and .geojson are not supported
        TextAsset jsonData = Resources.Load<TextAsset>(geoJSONFilePath);
        string geoJSONText = jsonData.text;

        JSONNode geoJSONData = JSON.Parse(geoJSONText);
        return geoJSONData;
    }

}
