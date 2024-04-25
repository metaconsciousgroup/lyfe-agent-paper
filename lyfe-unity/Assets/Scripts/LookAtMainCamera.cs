using UnityEngine;

public class LookAtMainCamera : BaseMonoBehaviour
{
    
    private static Transform lookTarget;
    
    
    protected override void Awake()
    {
        base.Awake();
        UpdateLook();
    }

    protected override void OnEnable()
    {
        base.OnEnable();
        UpdateLook();
    }

    private void Update()
    {
        UpdateLook();
    }

    private void LateUpdate()
    {
        UpdateLook();
    }
    
    private void UpdateLook()
    {
        if (lookTarget == null) lookTarget = Camera.main.transform;
        if (lookTarget != null) transform.rotation = Quaternion.LookRotation(transform.position - lookTarget.position);
    }
}
