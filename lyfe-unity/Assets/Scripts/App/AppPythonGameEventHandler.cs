using System.Collections;
using System.Linq;
using UnityEngine;

public class AppPythonGameEventHandler : MonoBehaviour
{
    [SerializeField] private SOAppConfig _config;    

    private SODebug GetDebug() => _config.GetEnvironment().GetDebugPython();

    public void ListenGameEvents(bool alter)
    {
        if (GetDebug().LogInfo)
            Debug.Log($"{GetType()}.ListenGameEvents({alter})".Color(GetDebug().GetColor()));

        AppGame game = App.Instance.GetGame();
        AppNetwork network = game.GetNetwork();
        AppAgents agents = game.GetAgents();

        agents.onAgentAdded.AlterListener(OnAgentAdded, alter);
        agents.onAgentRemoved.AlterListener(OnAgentRemoved, alter);

        network.onServerStarted.AlterListener(OnServerStarted, alter);
        network.onServerClientAdded.AlterListener(OnNetworkPlayerAdded, alter);
        network.onServerClientRemoved.AlterListener(OnNetworkPlayerRemoved, alter);
        network.onChatMessageProcessed.AlterListener(OnAppNetworkChatMessageProcessed, alter);
    }

    private void SendToPython(PythonSendOut value) {
        App.Instance.GetPythonWebSocket().SendToPython(value);
    }

    private void OnServerStarted()
    {
        Debug.Log("OnServerStarted");
        SendToPython(new PythonSendOutServerState(PythonSendOutServerState.ServerState.STARTED));

        AppGame game = App.Instance.GetGame();
        string sceneOverride = game.GetLoginData().sceneOverride;
        
        string sceneName = string.IsNullOrEmpty(sceneOverride) ? game.GetGameData().scene.name : sceneOverride;
        App.Instance.GetGame().GetNetwork().LoadSceneOnServer(sceneName, null, null);
    }

    /// <summary>
    /// Event handler when new agent is added.
    /// </summary>
    /// <param name="agentEntity"></param>
    private void OnAgentAdded(AgentEntity agentEntity)
    {
        AlterAgentEventListeners(agentEntity, true);
    }

    /// <summary>
    /// Event handler when agent is being removed.
    /// </summary>
    /// <param name="agentEntity"></param>
    private void OnAgentRemoved(AgentEntity agentEntity)
    {
        AlterAgentEventListeners(agentEntity, false);
    }

    private void AlterAgentEventListeners(AgentEntity agentEntity, bool alter)
    {
        if (agentEntity == null) return;
        agentEntity.onCharacterNavMeshAgentMoveEnded.AlterListener(OnAgentCharacterNavMeshAgentMoveEnded, alter);
    }

    private void OnAgentCharacterNavMeshAgentMoveEnded(AgentEntity agentEntity, NavigationPoint levelNavigationDestination)
    {
        if (levelNavigationDestination == null) return;
        string id = agentEntity.GetCharacter().GetUser().Id.GetValue();
        string destination = levelNavigationDestination.GetKey();

        SendToPython(new PythonSendOutAgentMoveEnded(id, destination));
    }

    private void OnNetworkPlayerAdded(ClientNetworkBehaviour client)
    {
        SendToPython(PythonSendOutPlayerAdded.From(client.GetCharacter()));
    }

    private void OnNetworkPlayerRemoved(ClientNetworkBehaviour client)
    {
        SendToPython(PythonSendOutPlayerRemoved.From(client.GetCharacter()));
    }

    private void OnAppNetworkChatMessageProcessed(ChatMessageData chatMessageData)
    {
        string[] locations = chatMessageData.author.GetNearByAreas().GetAll().Select<LyfeCreatorWorldArea, string>(i => i.GetKey()).ToArray();
        switch (chatMessageData.author.GetPermission())
        {
            case CharacterPermission.Player:
                {
                    if (chatMessageData.channelId == App.Instance.GetUI().GetView<UIViewChat>().GetDefaultChannelId())
                    {
                        SendToPython(PythonSendOutPlayerChatMessage.From(chatMessageData.author, chatMessageData.message));
                    }
                    else
                    {
                        SendToPython(PythonSendOutPlayerDirectMessage.From(chatMessageData, locations));
                    }

                    break;
                }
            case CharacterPermission.Agent:
                {
                    SendToPython(PythonSendOutAgentChatMessage.From(chatMessageData, locations));
                    break;
                }
        }
    }
}
