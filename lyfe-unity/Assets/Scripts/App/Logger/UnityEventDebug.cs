using UnityEngine;
using UnityEngine.Events;

[System.Serializable]
public class UnityEventDebug : UnityEvent<UnityEventDebug.Data>
{
    public class Data
    {
        public string condition;
        public string stackTrace;
        public LogType type;
            
        public Data(string condition, string stackTrace, LogType type)
        {
            this.condition = condition;
            this.stackTrace = stackTrace;
            this.type = type;
        }
    }
}
