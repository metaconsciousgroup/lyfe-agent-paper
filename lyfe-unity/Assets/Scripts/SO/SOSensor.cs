using UnityEngine;

[CreateAssetMenu(fileName = "Sensor - ", menuName = "SO/Sensor", order = 1)]
public class SOSensor : SO
{
    [SerializeField] private string _key;
    public string GetKey() => _key;
}
