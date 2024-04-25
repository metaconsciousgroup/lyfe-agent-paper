using UnityEngine;

[CreateAssetMenu(fileName = "Item - ", menuName = "SO/App/Item", order = 1)]
public class SOItem : SO
{
    [SerializeField] private string _title;
    [SerializeField] private ItemEntity _prefab;

    public string GetTitle() => _title;
    public string GetId() => this.name;
    public ItemEntity GetPrefab() => _prefab;
}
