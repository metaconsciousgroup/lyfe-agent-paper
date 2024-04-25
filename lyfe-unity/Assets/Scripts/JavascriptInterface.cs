using Sirenix.OdinInspector;
using UnityEngine;

/// <summary>
/// These functions will be called to directly set host name field on the UI so that users don't need to set it manually.
/// Both format should be able to handle wss:// without a port.
/// </summary>
public class JavascriptInterface : MonoBehaviour
{
    [Tooltip("Console color.")]
    [SerializeField] private Color _debugColor;
    
    /// <summary>
    /// Internal helper method to fetch default overrides object.
    /// </summary>
    /// <returns></returns>
    private NetworkData GetDefaultNetworkOverrides() => App.Instance.GetGame().GetNetwork().GetDefaultNetworkOverrides();

    /// <summary>
    /// Override network hostname.
    /// Example format "123.234.345.456"
    /// </summary>
    /// <param name="hostname"></param>
    [Button]
    public void SetHostname(string hostname)
    {
        Debug.Log($"{GetType().Name}.SetHostname({hostname})".Color(_debugColor));
        
        GetDefaultNetworkOverrides().SetHostName(hostname);
    }

    /// <summary>
    /// Override network hostProxy.
    /// Example format "example.domain.com/join?instance=&amp;amp;lt;uuid&amp;amp;gt;"
    /// </summary>
    /// <param name="hostProxy"></param>
    [Button]
    public void SetHostProxy(string hostProxy)
    {
        Debug.Log($"{GetType().Name}.SetHostProxy({hostProxy})".Color(_debugColor));
        
        GetDefaultNetworkOverrides().SetHostName(hostProxy);
    }

    /// <summary>
    /// Override network.
    /// </summary>
    /// <param name="hostName"></param>
    /// <param name="username"></param>
    [Button]
    public void SetNetwork(string hostName, string username)
    {
        Debug.Log($"{GetType().Name}.SetNetwork({hostName}, {username})".Color(_debugColor));

        NetworkData defaultOverrides = GetDefaultNetworkOverrides();
        
        defaultOverrides.SetHostName(hostName);
        defaultOverrides.SetUsername(username);
    }
    
}
