using System;
using System.Collections;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

public class AppLogger : BaseMonoBehaviour
{
    [SerializeField] private UnityEventDebug _logMessageReceived;
    
    protected override void OnEnable()
    {
        base.OnEnable();
        Application.logMessageReceived += OnApplicationLogMessageReceived;
    }

    protected override void OnDisable()
    {
        base.OnDisable();
        Application.logMessageReceived -= OnApplicationLogMessageReceived;
    }

    private void OnApplicationLogMessageReceived(string condition, string stackTrace, LogType type)
    {
        _logMessageReceived.Invoke(new UnityEventDebug.Data(condition, stackTrace, type));
    }

    
    
    [Button]
    public void TestError()
    {
        Debug.LogError("Test error message.");
    }
    [Button]
    public void TestWarning()
    {
        Debug.LogWarning("Test warning message.");
    }
    [Button]
    public void TestException()
    {
        throw new UnityException("Test Exception message");
    }
    [Button]
    public void TestAssertion()
    {
        Debug.LogAssertion("Test Assertion message.");
    }
}
