using System;
using System.Collections;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using JetBrains.Annotations;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using Sirenix.OdinInspector;
using UnityEngine;

public class AppPythonWebSocket : AppPython
{
    [Title("WebSocket")]
    [ReadOnly, ShowInInspector] private ConnectorData _connectorData;
    [Space]
    [ReadOnly, ShowInInspector] private bool _isConnecting;
    [ReadOnly, ShowInInspector] private bool _initialized;

    private ClientWebSocket _clientWebSocket = new();
    private CancellationTokenSource cancellationTokenSource = new();

    private const string ArgUrl = "-websocketUrl";
    private const string ArgPort = "-websocketPort";
    private const string ArgBufferSize = "-websocketBufferSize";
    private const string ArgSimId = "-simulationId";

    protected override void Awake()
    {
        base.Awake();
        UpdateServerWebsocketSettings();
    }

    protected override void OnDestroy()
    {
        base.OnDestroy();
        CloseClientWebsocket();
    }

    private void Update()
    {
        if (_clientWebSocket.State != WebSocketState.Open && _initialized && !_isConnecting && App.Instance.GetConfig().GetEnvironment().GetKind() != AppKind.Client)
        {
            string json = JsonConvert.SerializeObject(_connectorData, Formatting.Indented, new StringEnumConverter());
            Debug.Log($"Python server websocket settings: {json}".Color(GetDebug().GetColor()));
            Debug.Log($"WebSocket connection is closed after initialized. State: {_clientWebSocket.State}".Color(GetDebug().GetColor()));
            StartCoroutine(RestartConnection());
        }
    }

    private void UpdateServerWebsocketSettings()
    {
        _connectorData = CollectConnectorData();
    }

    private void CloseClientWebsocket()
    {
        cancellationTokenSource.Cancel();
        if (_clientWebSocket != null)
        {
            if (_isConnecting || _initialized)
            {
                _clientWebSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
                _clientWebSocket.Dispose();
            }
        }
        _clientWebSocket = new ClientWebSocket();
    }

    protected override IEnumerator InitializeConnection()
    {
        if (App.Instance.GetConfig().GetEnvironment().GetKind() == AppKind.Client)
        {
            Debug.Log("Client app kind. Skipping Python websocket initialization.");
            yield break;
        }

        // Start the connection process
        yield return StartCoroutine(ConnectWebSocket());

        if (_clientWebSocket.State == WebSocketState.Open)
        {
            Debug.Log("WebSocket connection established.");
        }
        else
        {
            Debug.LogError("Failed to establish WebSocket connection within 300 seconds.");
        }
        Initialize_Internal();
        _initialized = true;

        yield return StartCoroutine(ReceiveMessage());
    }

    private IEnumerator RestartConnection()
    {
        // TODO log out all existing players.
        Debug.Log("Restarting connection...");
        _clientWebSocket.Dispose();
        _clientWebSocket = new ClientWebSocket(); // Reset the WebSocket
        yield return StartCoroutine(ConnectWebSocket());
        yield return StartCoroutine(ReceiveMessage());
    }

    private IEnumerator ConnectWebSocket()
    {
        _isConnecting = true;
        var connectTask = _clientWebSocket.ConnectAsync(_connectorData.GetUri(), cancellationTokenSource.Token);

        int safetyCounter = 0;
        const int maxAttempts = 100; // Adjust as needed
        do
        {
            Debug.Log($"Waiting for communicator to turn on. Safety counter: {safetyCounter}".Color(GetDebug().GetColor()));
            if (_clientWebSocket.State == WebSocketState.Open)
            {
                Debug.Log("WebSocket connection already established.");
                yield break;
            }
            if (!connectTask.IsCompleted)
            {
                yield return new WaitForSeconds(2f);
                continue;
            }
            if (connectTask.IsCompleted && connectTask.Status != System.Threading.Tasks.TaskStatus.RanToCompletion)
            {
                _clientWebSocket.Dispose();
                _clientWebSocket = new ClientWebSocket(); // Reset the WebSocket
            }
            connectTask = _clientWebSocket.ConnectAsync(_connectorData.GetUri(), cancellationTokenSource.Token);
            safetyCounter++;
        } while (_clientWebSocket.State != WebSocketState.Open && safetyCounter < maxAttempts);

        if (!connectTask.IsCompleted)
        {
            cancellationTokenSource.Cancel();
            _clientWebSocket.Dispose();
            _clientWebSocket = new ClientWebSocket(); // Reset the WebSocket
        }
        _isConnecting = false;
    }
    protected override void Initialize_Internal_Subclass()
    {
        // Nothing to do here
    }

    private IEnumerator ReceiveMessage()
    {
        // TODO JSON is too verbose. Use binary format instead.
        ArraySegment<byte> buffer = new ArraySegment<byte>(new byte[_connectorData.bufferSize]);
        WebSocketReceiveResult result = null;

        Debug.Log($"{GetType()}.ReceiveMessage".Color(GetDebug().GetColor()));
        while (_clientWebSocket.State == WebSocketState.Open)
        {
            var receive = _clientWebSocket.ReceiveAsync(buffer, CancellationToken.None);
            yield return new WaitUntil(() => receive.IsCompleted);

            result = receive.Result;
            if (result.MessageType == WebSocketMessageType.Text)
            {
                string message = Encoding.UTF8.GetString(buffer.Array, 0, result.Count);
                ReceiveMessageFromPython(message);
            }

            if (result.MessageType == WebSocketMessageType.Close)
            {
                break;
            }
        }
        Debug.Log($"{GetType()}.ReceiveMessage: WebSocket closed.".Color(GetDebug().GetColor()));
    }

    protected override void SendToPython_Internal(string message)
    {
        if (_clientWebSocket.State == WebSocketState.Open)
        {
            ArraySegment<byte> buffer = new ArraySegment<byte>(Encoding.UTF8.GetBytes(message));
            var send = _clientWebSocket.SendAsync(buffer, WebSocketMessageType.Text, true, CancellationToken.None);
            StartCoroutine(WaitForSend(send));
        }
    }

    private IEnumerator WaitForSend(System.Threading.Tasks.Task sendTask)
    {
        yield return new WaitUntil(() => sendTask.IsCompleted);
    }

    private ConnectorData CollectConnectorData()
    {
        CommandLineArgs data = CollectCommandLineArgs();
        return new ConnectorData(data);
    }

    /// <summary>
    /// Collect command-line arguments.
    /// </summary>
    /// <returns></returns>
    private CommandLineArgs CollectCommandLineArgs()
    {
        CommandLineArgs data = new CommandLineArgs();

        string[] args = Environment.GetCommandLineArgs();

        int argsLength = args.Length;

        for (int i = 0; i < args.Length; i++)
        {
            string arg = args[i];
            int ii = i + 1;
            bool haveNext = argsLength > ii;

            if (!haveNext) break;

            switch (arg)
            {
                case ArgUrl:
                    {
                        data.url = args[ii];
                        break;
                    }
                case ArgPort:
                    {
                        data.port = args[ii];
                        break;
                    }
                case ArgBufferSize:
                    {
                        string nextArg = args[ii];

                        if (!int.TryParse(nextArg, out int result))
                            Debug.LogWarning($"Failed to parse bufferSize string '{nextArg}' to int");
                        else
                            data.bufferSize = result;
                        break;
                    }
                case ArgSimId:
                    {
                        data.simulationId = args[ii];
                        break;
                    }
            }
        }

        return data;
    }

    private class ConnectorData
    {
        [ReadOnly, ShowInInspector] public readonly string url;
        [ReadOnly, ShowInInspector] public readonly string port;
        [ReadOnly, ShowInInspector] public readonly int bufferSize;
        [ReadOnly, ShowInInspector] public readonly string simulationId;
        [ReadOnly, ShowInInspector] public readonly string uriString;
        [ReadOnly, ShowInInspector] private CommandLineArgs _commandLineArgs;
        private Uri _uri;
        [Space]
        [ReadOnly, ShowInInspector] private string _defaultUrl = "127.0.0.1";
        [ReadOnly, ShowInInspector] private string _defaultPort = "8765";
        [ReadOnly, ShowInInspector] private string _defaultSimulationId = "01234";
        [ReadOnly, ShowInInspector] private int _defaultBufferSize = 65536;

        public ConnectorData(CommandLineArgs commandLineArgs)
        {
            _commandLineArgs = commandLineArgs;
            url = commandLineArgs.url ?? _defaultUrl;
            port = commandLineArgs.port ?? _defaultPort;
            bufferSize = commandLineArgs.bufferSize ?? _defaultBufferSize;
            simulationId = commandLineArgs.simulationId ?? _defaultSimulationId;
            uriString = simulationId.Length == 0 ?
                $"ws://{url}:{port}" :
                $"ws://{url}:{port}/agent-actions?simulation_id={simulationId}";
            _uri = new Uri(uriString);
        }

        public Uri GetUri() => _uri;
    }

    private class CommandLineArgs
    {
        [CanBeNull] public string url;
        [CanBeNull] public string port;
        [CanBeNull] public string simulationId;
        public int? bufferSize;
    }
}