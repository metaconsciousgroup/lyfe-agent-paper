using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.Events;

[System.Serializable]
public class UnityEventLoginRequest : UnityEvent<UnityEventLoginRequest.Data>
{
    public class Data
    {
        public string networkAddress;
        public ushort portStandalone;
        public ushort portWeb;
        public bool dedicatedHost;
        public string username;
        public InDataCharacter character;
        public string sceneOverride;

        public Data(
            string networkAddress,
            ushort portStandalone,
            ushort portWeb,
            bool dedicatedHost,
            string username,
            InDataCharacter character,
            string sceneOverride)
        {
            this.networkAddress = networkAddress;
            this.portStandalone = portStandalone;
            this.portWeb = portWeb;
            this.dedicatedHost = dedicatedHost;
            this.username = username;
            this.character = character;
            this.sceneOverride = sceneOverride;
        }

        public override string ToString()
        {
            return JsonConvert.SerializeObject(this);
        }
    }
}
