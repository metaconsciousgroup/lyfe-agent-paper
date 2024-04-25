using UnityEngine;

[System.Serializable]
public class NetworkData
{
    [SerializeField] private string _hostName;
    [SerializeField] private string _portStandalone;
    [SerializeField] private string _portWeb;
    [SerializeField] private string _username;

    public string hostName => _hostName;
    public string portStandalone => _portStandalone;
    public string portWeb => _portWeb;
    public string username => _username;

    public NetworkData() { }

    public NetworkData(string hostName, ushort portStandalone, ushort portWeb, string username) : this(
        hostName,
        portStandalone.ToString(),
        portWeb.ToString(),
        username)
    { }

    public NetworkData(string hostName, string portStandalone, string portWeb, string username)
    {
        _hostName = hostName;
        _portStandalone = portStandalone;
        _portWeb = portWeb;
        _username = username;
    }

    public void SetHostName(string value) => _hostName = value;

    public void SetPortStandalone(string value) => _portStandalone = value;

    public void SetPortWeb(string value) => _portWeb = value;
    public void SetUsername(string value) => _username = value;
}
