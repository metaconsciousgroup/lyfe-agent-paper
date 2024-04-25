using UnityEngine;

[CreateAssetMenu(fileName = "Prefabs", menuName = "SO/App/Prefabs", order = 1)]
public class SOPrefabs : SO
{
    [SerializeField] private Smartphone _smartphone;

    public Smartphone GetSmartphone() => _smartphone;
}
