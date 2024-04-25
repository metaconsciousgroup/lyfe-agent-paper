using UnityEngine;

[CreateAssetMenu(fileName = "Emote - ", menuName = "SO/App/Emote", order = 1)]
public class SOEmote : SO
{
    [SerializeField] private EmoteKind _kind;
    [SerializeField] private Sprite _sprite;

    public EmoteKind GetKind() => _kind;
    public int GetId() => (int)_kind;
    public string GetKey() => name;
    public Sprite GetSprite() => _sprite;
}
