using UnityEngine;

[CreateAssetMenu(fileName = "Sensors", menuName = "SO/Sensors", order = 1)]
public class SOSensors : SO
{
    [SerializeField] private SOSensor _auditory;
    [SerializeField] private SOSensor _rayVision;
    [SerializeField] private SOSensor _item;

    public SOSensor GetAuditory() => _auditory;
    
    public SOSensor GetRayVision() => _rayVision;
    
    public SOSensor GetItem() => _item;
}
