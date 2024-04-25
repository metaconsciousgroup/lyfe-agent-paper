using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class InputChecker : BaseMonoBehaviour
{
    private bool _canRotateCamera;

    protected override void Start()
    {
        UnfocusFromChat();
    }
    
    public bool GetCanRotateCamera()
    {
        return _canRotateCamera;
    }

    public void FocusOnChat()
    {
        _canRotateCamera = false;
    }

    public void UnfocusFromChat()
    {
        _canRotateCamera = true;
    }
}
