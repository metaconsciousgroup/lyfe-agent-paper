using UnityEngine;

public class ContantRotate : BaseMonoBehaviour
{
    [SerializeField] private Vector3 _speed;
    
    void Update()
    {
        transform.Rotate(_speed * Time.deltaTime);
    }
}
