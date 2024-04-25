using System.Collections.Generic;
using System.Linq;
using FishNet.Connection;
using FishNet.Object;
using FishNet.Object.Synchronizing;
using FishNet.Transporting;
using Sirenix.OdinInspector;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Events;

public class ClientNetworkBehaviour : NetworkEntity
{
    [Title("Client")]
    

    [SyncVar(Channel = Channel.Reliable, ReadPermissions = ReadPermission.Observers, OnChange = nameof(OnClient_Username_Change))]
    [ReadOnly, ShowInInspector] private string _username = string.Empty;

    [SyncVar(Channel = Channel.Reliable, ReadPermissions = ReadPermission.Observers, OnChange = nameof(OnClient_CharacterModelPath_Change))]
    [ReadOnly, ShowInInspector] private string _characterModelPath = string.Empty;

    [SyncVar(Channel = Channel.Reliable, ReadPermissions = ReadPermission.Observers, OnChange = nameof(OnClient_Permission_Change))]
    [ReadOnly, ShowInInspector] private CharacterPermission _permission = CharacterPermission.Undefined;

    [SyncVar(Channel = Channel.Reliable, ReadPermissions = ReadPermission.Observers, OnChange = nameof(OnClient_LookAtNetworkId_Change))]
    [ReadOnly, ShowInInspector] private string _lookAtEntityId;


    [SerializeField] private CharacterEntity _character;
    

    public CharacterEntity GetCharacter() => _character;
    public UserEntity GetUser() => _character.GetUser();

    private SODebug GetDebug() => GetConfig().GetEnvironment().GetDebugNetworkClient();
    
    public override Transform GetExpectedHierarchyParent() => App.Instance.GetGame().GetCharacters().transform;

    private static readonly List<ClientNetworkBehaviour> Clients = new();

    public override bool GetGizmoDebuggerInfo(out string text)
    {
        text = string.Empty;

        if (!GetConfig().GetEnvironment().showCharacterInformation) return false;
        
        UserEntity u = GetUser();

        string GetClientIdText(int id)
        {
            Color color = id >= 0 ? Color.cyan : Color.red;
            return $"[{id}]".Color(color);
        }

        string GetPermissionText(CharacterPermission permission)
        {
            Color color = Color.gray;
            switch (permission)
            {
                case CharacterPermission.Player:
                {
                    color = Color.cyan;
                    break;
                }
                case CharacterPermission.Agent:
                {
                    color = Color.red;
                    break;
                }
            }
            return $"[{permission}]".Color(color);
        }
        
        string c = GetClientIdText(OwnerId);
        string role = GetPermissionText(_character.GetPermission());
        
        text = $"[{GetSyncId()}] {c} [{u.Username.GetValue()}] {role}";
        return true;
    }

    protected override void Awake()
    {
        base.Awake();
        Clients.Add(this);
    }

    private void OnDestroy()
    {
        Clients.Remove(this);
    }
    
    /**s
     * Override.
     */
    public override bool GetLookAtDestinationPoint(out Vector3 point) => _character.GetReadyPlayerMeAvatarRenderer().GetLookAtDestinationPoint(out point);

    public void OnAvatarRendererEmote(int emoteId)
    {
        // This was ran on the server - send to everyone.
        if(IsServer)
        {
            Server_BroadcastEmote(this, emoteId, false);
        }
        
        // Send to server only if we did this - send to everyone except us.
        else if(IsOwner){
            // Send request to server.
            ServerRpc_BroadcastEmoteToOthers(this, emoteId);
        }
    }

    /// <summary>
    /// Called on the client after initializing this object.
    /// </summary>
    public override void OnStartClient()
    {
        base.OnStartClient();
        //Debug.Log($"{GetType().Name}.OnStartClient IsOwner:{IsOwner} IsServer:{IsServer} IsClient:{IsClient} IsClientOnly:{IsClientOnly}");

        if (_character.GetPermission() != CharacterPermission.Agent)
        {
            _character.SetupAsPlayer(IsOwner && IsClient);
        }

        AppGame game = App.Instance.GetGame();

        if (IsOwner)
        {
            Player player = game.GetPlayer();
            player.SetCharacter(_character);

            if (GetDebug().LogInfo)
                Debug.Log("Spawned your player".Color(GetDebug().GetColor()));
        }
        else
        {
            //Debug.Log("Spawned other player");
        }

        onStartClient.Invoke(this);
    }

    public override void OnStopClient()
    {
        base.OnStopClient();

        if (GetDebug().LogInfo)
            Debug.Log($"Client id[{LocalConnection.ClientId}] stopped".Color(GetDebug().GetColor()));
    }

    /// <summary>
    /// Called on the server after initializing this object.
    /// SyncTypes modified before or during this method will be sent to clients in the spawn message.
    /// </summary> 
    public override void OnStartServer()
    {
        base.OnStartServer();
        onStartServer.Invoke(this);

        if (_permission == CharacterPermission.Player)
        {
            App.Instance.GetGame().GetNetwork().onServerClientAdded.Invoke(this);
        }
    }

    /// <summary>
    /// Called on the server before deinitializing this object.
    /// </summary>
    public override void OnStopServer()
    {
        base.OnStopServer();

        if (_permission == CharacterPermission.Player)
        {
            App.Instance.GetGame().GetNetwork().onServerClientRemoved.Invoke(this);
        }
    }

    public void SetPositionAndRotation(Vector3 position, float rotation)
    {
        _character.transform.position = position;
        _character.SetInstantRotation(rotation);
    }


    protected override void OnSyncIdChanged(string prev, string next, bool asServer)
    {
        GetUser().Id.SetValue(next);
    }

    

    private void OnClient_Username_Change(string prev, string next, bool asServer)
    {
        GetUser().Username.SetValue(next);
    }

    private void OnClient_CharacterModelPath_Change(string prev, string next, bool asServer)
    {
        _character.GetReadyPlayerMeAvatarRenderer().LoadAvatar(next);
    }

    private void OnClient_Permission_Change(CharacterPermission prev, CharacterPermission next, bool asServer)
    {
        _character.SetPermission(next);
    }

    private void OnClient_LookAtNetworkId_Change(string prev, string next, bool asServer)
    {
        if (App.Instance.GetGame().GetEntities().GetById(next, out NetworkEntity networkEntity))
        {
            _character.SetLookAtDestination(networkEntity);
        }
        else
        {
            _character.ClearLookAtDestination();
        }
    }

    public void FromServer_SetPermission(CharacterPermission value)
    {
        _permission = value;
        _character.SetPermission(value);
    }

    public void FromServer_SetUsername(string value)
    {
        _username = value;
        GetUser().Username.SetValue(value);
    }

    public void FromServer_SetCharacterModelPath(string value)
    {
        _characterModelPath = value;
        _character.GetReadyPlayerMeAvatarRenderer().LoadAvatar(value);
    }

    public void FromServer_LookAtSet(NetworkEntity networkEntity)
    {
        // Trying to look at himself - this is not supported
        if (networkEntity != null && networkEntity == _character)
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning("Look at character target is himself, this is not supported.".Color(GetDebug().GetColor()));
            return;
        }
        
        if (GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.FromServer_LookAtSet IsServer[{IsServer}] User '{GetUser().Username.GetValue()}' setting look at target to '{networkEntity?.GetSyncId() ?? "null"}'.".Color(GetDebug().GetColor()));
            
        _lookAtEntityId = networkEntity.GetSyncId();
        _character.SetLookAtDestination(networkEntity);
    }

    public void FromServer_LookAtClear()
    {
        _character.ClearLookAtDestination();
        _lookAtEntityId = null;
    }

    public void BroadcastChatMessage(ChatMessageData chatMessageData)
    {
        if (chatMessageData == null) return;

        if (chatMessageData.author != GetCharacter())
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning("You are trying to send chat message from wrong user.".Color(GetDebug().GetColor()));
            return;
        }

        string message = chatMessageData.message;
        string channelId = chatMessageData.channelId;
        bool isServer = IsServer;

        if (GetDebug().LogInfo)
            Debug.Log($"{GetType().Name}.BroadcastChatMessage IsServer[{isServer}] User '{GetUser().Username.GetValue()}' broadcasting chat message '{message}' in channel [{channelId}].".Color(GetDebug().GetColor()));


        // Executed on server
        if (isServer)
        {
            if (GetCharacter().IsMe())
            {
                App.Instance.GetGame().ShowChatMessage(chatMessageData);
            }

            string senderUserId = GetUser().Id.GetValue();

            HashSet<CharacterEntity> receivers = new HashSet<CharacterEntity>(chatMessageData.receiverPlayers);

            // This means this was called on server, but for different player.
            if (GetCharacter().IsPlayerButNotMe())
            {
                receivers.Add(GetCharacter());
            }

            foreach (CharacterEntity receiverPlayer in receivers)
            {
                if (receiverPlayer == null) continue;
                receiverPlayer.GetClient().TargetRpc_ReceiveChatMessage(receiverPlayer.GetClient().Owner, senderUserId, message, channelId);
            }

            App.Instance.GetGame().GetNetwork().onChatMessageProcessed.Invoke(chatMessageData);
        }

        // Executed on client
        else
        {
            App.Instance.GetGame().ShowChatMessage(chatMessageData);

            FromClient_ServerRpc_BroadcastChatMessage(
                this,
                message,
                channelId,
                chatMessageData.receiverPlayers.Select(i => i.GetUser().Id.GetValue()).ToArray(),
                chatMessageData.receiverAgents.Select(i => i.GetUser().Id.GetValue()).ToArray());
        }
    }

    /// <summary>
    /// Broadcast chat message from client.
    /// </summary>
    /// <param name="sender"></param>
    /// <param name="message"></param>
    /// <param name="channelId"></param>
    /// <param name="targets"></param>
    [ServerRpc(RequireOwnership = true)]
    private void FromClient_ServerRpc_BroadcastChatMessage(ClientNetworkBehaviour sender, string message, string channelId, string[] receiverPlayerIds, string[] receiverAgentIds)
    {
        if (sender == null)
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning("Server received chat message from sender which no longer exists.".Color(GetDebug().GetColor()));
            return;
        }

        CharacterEntity senderCharacter = sender.GetCharacter();
        if (senderCharacter == null)
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning("Server received chat message from user which no longer exists.".Color(GetDebug().GetColor()));
            return;
        }

        // TODO: check on server how close these targets actually are to sender, considering possible delay and de-isServer.

        string senderUserId = sender.GetUser().Id.GetValue();
        HashSet<CharacterEntity> receiverPlayers = new HashSet<CharacterEntity>();
        HashSet<CharacterEntity> receiverAgents = new HashSet<CharacterEntity>();

        if (receiverPlayerIds != null)
        {
            // Iterate over target player, validate each player on server and send RPC.
            foreach (string receiverPlayerId in receiverPlayerIds)
            {
                // Check if target player id is not empty.
                if (string.IsNullOrEmpty(receiverPlayerId))
                {
                    if (GetDebug().LogWarning)
                        Debug.LogWarning("Receiver player id is null or empty, skipping..".Color(GetDebug().GetColor()));
                    continue;
                }

                // Check if target player even exists on server.
                if (!App.Instance.GetGame().GetCharacters().GetById(receiverPlayerId, out CharacterEntity receiverPlayerCharacter))
                {
                    if (GetDebug().LogWarning)
                        Debug.LogWarning($"Target player with id '{receiverPlayerId}' does not exists, skipping..".Color(GetDebug().GetColor()));
                    continue;
                }

                // Check if receiver is even player.
                if (receiverPlayerCharacter.GetPermission() != CharacterPermission.Player)
                {
                    if (GetDebug().LogWarning)
                        Debug.LogWarning($"Target player with id '{receiverPlayerId}' permission is not '{CharacterPermission.Player}', skipping..".Color(GetDebug().GetColor()));
                    return;
                }

                receiverPlayers.Add(receiverPlayerCharacter);
                TargetRpc_ReceiveChatMessage(receiverPlayerCharacter.GetClient().Owner, senderUserId, message, channelId);
            }
        }

        if (receiverAgentIds != null)
        {
            // Iterate over target agents, validate each agent on server and include in final list.
            foreach (string receiverAgentId in receiverAgentIds)
            {
                // Check if target player id is not empty.
                if (string.IsNullOrEmpty(receiverAgentId))
                {
                    if (GetDebug().LogWarning)
                        Debug.LogWarning("Receiver agent id is null or empty, skipping..".Color(GetDebug().GetColor()));
                    continue;
                }

                // Check if target agent even exists on server.
                if (!App.Instance.GetGame().GetAgents().GetAgentById(receiverAgentId, out AgentEntity receiverAgent))
                {
                    if (GetDebug().LogWarning)
                        Debug.LogWarning($"Target agent with id '{receiverAgentId}' does not exists, skipping..".Color(GetDebug().GetColor()));
                    continue;
                }

                receiverAgents.Add(receiverAgent.GetCharacter());
            }
        }

        ChatMessageData chatMessageData = ChatMessageData.From(senderCharacter, message, channelId, receiverPlayers, receiverAgents);
        App.Instance.GetGame().GetNetwork().onChatMessageProcessed.Invoke(chatMessageData);
    }

    [TargetRpc]
    private void TargetRpc_ReceiveChatMessage(NetworkConnection target, string senderUserId, string message, string channelId)
    {

        if (!App.Instance.GetGame().GetCharacters().GetById(senderUserId, out CharacterEntity senderCharacter))
        {
            Debug.LogWarning($"Received chat message from user id '{senderUserId}' which does not exist locally.");
            return;
        }

        UserEntity user = senderCharacter.GetUser();

        if (GetDebug().LogInfo)
            Debug.Log($"Received chat message IsServer[{IsServer}] from '{user.Username.GetValue()}': {message}".Color(GetDebug().GetColor()));

        ChatMessageData chatMessageData = ChatMessageData.From(senderCharacter, message, channelId);
        App.Instance.GetGame().ShowChatMessage(chatMessageData);
    }

    public void BroadcastAgentMove(AgentMoveData agentMoveData)
    {
        if (agentMoveData == null) return;

        if (agentMoveData.agent != GetCharacter())
        {
            if (GetDebug().LogWarning)
                Debug.LogWarning("You are trying to send chat message from wrong user.".Color(GetDebug().GetColor()));
            return;
        }

        string locationName = agentMoveData.locationName;
        bool isServer = IsServer;


        // Agent moving should only be called on server.
        if (isServer)
        {
            if (GetDebug().LogInfo)
                Debug.Log($"{GetType().Name}.BroadcastAgentMove User '{GetUser().Username.GetValue()}' broadcasting agent moving to '{locationName}'.".Color(GetDebug().GetColor()));


            if (GetCharacter().IsMe())
            {
                App.Instance.GetGame().ShowAgentMove(agentMoveData, GetCharacter());
            }

            string senderUserId = GetUser().Id.GetValue();

            HashSet<CharacterEntity> receivers = new HashSet<CharacterEntity>(agentMoveData.receiverPlayers);

            // This means this was called on server, but for different player.
            if (GetCharacter().IsPlayerButNotMe())
            {
                receivers.Add(GetCharacter());
            }

            foreach (CharacterEntity receiverPlayer in receivers)
            {
                if (receiverPlayer == null) continue;
                receiverPlayer.GetClient().TargetRpc_ReceiveAgentMove(receiverPlayer.GetClient().Owner, senderUserId, locationName);
            }

            App.Instance.GetGame().GetNetwork().onAgentMoveProcessed.Invoke(agentMoveData);
        }
        else
        {
            Debug.LogError("Agent moving should only be called on server.");
        }
    }

    [TargetRpc]
    private void TargetRpc_ReceiveAgentMove(NetworkConnection target, string senderUserId, string locationName)
    {

        if (!App.Instance.GetGame().GetCharacters().GetById(senderUserId, out CharacterEntity senderCharacter))
        {
            Debug.LogWarning($"Received chat message from user id '{senderUserId}' which does not exist locally.");
            return;
        }

        UserEntity user = senderCharacter.GetUser();

        if (GetDebug().LogInfo)
            Debug.Log($"Received agent move IsServer[{IsServer}] from '{user.Username.GetValue()}': {locationName}".Color(GetDebug().GetColor()));

        AgentMoveData agentMoveData = AgentMoveData.From(senderCharacter, locationName);
        foreach (CharacterEntity player in senderCharacter.GetNearByCharacters().GetAllWithPermission(CharacterPermission.Player))
        {
            if (player.IsMe())
            {
                App.Instance.GetGame().ShowAgentMove(agentMoveData, player);
            }
        }
    }

    [ServerRpc(RequireOwnership = true)]
    private void ServerRpc_BroadcastEmoteToOthers(ClientNetworkBehaviour sender, int emoteId)
    {
        Server_BroadcastEmote(sender, emoteId, false);
    }
    
    [TargetRpc]
    private void TargetRpc_ReceiveEmote(NetworkConnection target, string senderUserId, int emoteId)
    {
        if (!App.Instance.GetGame().GetCharacters().GetById(senderUserId, out CharacterEntity senderCharacter))
        {
            Debug.LogWarning($"Received emote from user id '{senderUserId}' does not exist locally.");
            return;
        }
        
        if (GetDebug().LogInfo)
            Debug.Log($"Received rpc on character '{_character.GetUser().Username.GetValue()}' about original sender: {senderCharacter.GetUser().Username.GetValue()} doing emote {emoteId}".Color(GetDebug().GetColor()));

        senderCharacter.ExecuteEmote(emoteId, false);
    }

    private void Server_BroadcastEmote(ClientNetworkBehaviour sender, int emoteId, bool includeSender)
    {
        if (!IsServer) return;
        
        string senderUserId = sender.GetUser().Id.GetValue();

        // Send to clients
        foreach (CharacterEntity targetCharacter in App.Instance.GetGame().GetCharacters().GetAll())
        {
            // This is not player
            if(targetCharacter.GetPermission() != CharacterPermission.Player) continue;
            if(targetCharacter.IsMe()) continue;
            
            ClientNetworkBehaviour targetClient = targetCharacter.GetClient();
            
            // This client is the one who sent the message
            if(!includeSender && targetClient.OwnerId == sender.OwnerId) continue;

            Debug.Log($"Server: character '{sender.GetCharacter().GetUser().Username.GetValue()}' did emote {emoteId} and is sending to {targetCharacter.GetUser().Username.GetValue()}");
            TargetRpc_ReceiveEmote(targetClient.Owner, senderUserId, emoteId);
        }

        // Display the emote on the server
        sender.GetCharacter().ExecuteEmote(emoteId, false);
    }

    
}
