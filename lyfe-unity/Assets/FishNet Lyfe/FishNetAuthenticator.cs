using System;
using System.Collections.Generic;
using FishNet.Authenticating;
using FishNet.Broadcast;
using FishNet.Connection;
using FishNet.Managing;
using Sirenix.OdinInspector;
using UnityEngine;

public class FishNetAuthenticator : Authenticator
{
    [SerializeField] private SOAppConfig _config;
    [Tooltip("If true, only then new clients will be able to connect.")]
    [SerializeField] private bool _allowClientAuthentications;
    public override event Action<NetworkConnection, bool> OnAuthenticationResult;

    /// <summary>
    /// Authentications map ClientId -> auth data
    /// </summary>
    [ReadOnly, ShowInInspector]
    private Dictionary<int, AuthRequest> _authentications = new();
    
    public struct AuthRequest : IBroadcast
    {
        public string username;
        public string characterModelPath;
    }
    
    public struct AuthResponse : IBroadcast
    {
        public bool success;
    }
    
    private SODebug GetDebug() => _config.GetEnvironment().GetDebugAuthentication();

    /// <summary>
    /// Set allowance for client to connect (Server-Only).
    /// </summary>
    /// <param name="value"></param>
    public void SetAllowClientAuthentications(bool value)
    {
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.SetAllowClientAuthentications({value})".Color(GetDebug().GetColor()));
        _allowClientAuthentications = value;
    }
    
    
    /// <summary>
    /// Initializes this script for use.
    /// </summary>
    /// <param name="networkManager"></param>
    public override void InitializeOnce(NetworkManager networkManager)
    {
        base.InitializeOnce(networkManager);
        //Listen for connection state of local server to set hash.
        
        //Listen for broadcast from client. Be sure to set requireAuthentication to false.
        base.NetworkManager.ServerManager.RegisterBroadcast<AuthRequest>(OnAuthRequest, false);
        
        //Listen to response from server.
        base.NetworkManager.ClientManager.RegisterBroadcast<AuthResponse>(OnAuthResponse);
    }

    /// <summary>
    /// Request authentication (Client-Only).
    /// </summary>
    /// <param name="request"></param>
    public void Authenticate(AuthRequest request)
    {
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.Authenticate".Color(GetDebug().GetColor()));
        base.NetworkManager.ClientManager.Broadcast(request);
    }
    
    /// <summary>
    /// Called on server when received client authentication request.
    /// </summary>
    /// <param name="conn">Client connection.</param>
    /// <param name="request">Client authentication request data.</param>
    private void OnAuthRequest(NetworkConnection conn, AuthRequest request)
    {
        //Not accepting host authentications. This could be an attack.
        if (!_allowClientAuthentications)
        {
            if(GetDebug().LogWarning)
                Debug.LogWarning($"{GetType().Name}.OnAuthRequest server authentication is disabled, disconnecting client[{conn.ClientId}]..".Color(GetDebug().GetColor()));
            conn.Disconnect(true);
            return;
        }
        
        /* If client is already authenticated this could be an attack. Connections
         * are removed when a client disconnects so there is no reason they should
         * already be considered authenticated. */
        if (conn.Authenticated)
        {
            if(GetDebug().LogWarning)
                Debug.LogWarning($"{GetType().Name}.OnAuthRequest client client[{conn.ClientId}] already authenticated, disconnecting..".Color(GetDebug().GetColor()));
            conn.Disconnect(true);
            return;
        }

        string u = request.username;
        string cmp = request.characterModelPath;
        
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.OnAuthRequest username[{u.ToStringNullable()}] character[{cmp.ToStringNullable()}]".Color(GetDebug().GetColor()));

        bool usernameValid = !string.IsNullOrEmpty(u);
        bool characterModelPathValid = !string.IsNullOrEmpty(cmp);

        bool success = usernameValid && characterModelPathValid;

        AuthResponse response = new AuthResponse()
        {
            success = success
        };

        if (success)
        {
            _authentications.Add(conn.ClientId, request);
        }

        OnAuthenticationResult?.Invoke(conn, success);
        base.NetworkManager.ServerManager.Broadcast(conn, response, false);
    }
    
    /// <summary>
    /// Called on client when received authentication response.
    /// </summary>
    /// <param name="response">Response data.</param>
    private void OnAuthResponse(AuthResponse response)
    {
        if(GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.OnAuthResponse success[{response.success}]".Color(GetDebug().GetColor()));
    }

    /// <summary>
    /// Fetch client authentication data (Server-Only).
    /// </summary>
    /// <param name="conn">Client connection.</param>
    /// <param name="request">Optional result.</param>
    /// <returns>Returns true if authentication data exist for the given connection</returns>
    public bool GetAuthenticationData(NetworkConnection conn, out AuthRequest request)
    {
        request = new AuthRequest();
        if (conn == null) return false;
        if (!_authentications.ContainsKey(conn.ClientId)) return false;

        request = _authentications[conn.ClientId];
        return true;
    }
    
}
