using UnityEngine;

public class TriggerTarget : BaseMonoBehaviour
{
    [SerializeField] private GameObject _target;
    
    public GameObject GetTarget() => _target;
}
