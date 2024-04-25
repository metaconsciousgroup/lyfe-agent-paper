using UnityEngine;

public class IdentifierState : BaseMonoBehaviour
{
    [SerializeField] private Identifier _identifierAllow;
    [SerializeField] private Identifier _identifierBlock;

    
    public bool IsAllowed() => !_identifierBlock.Contains() && _identifierAllow.Contains();
    
    
    public void AlterAllow(Identifier identifier, bool alter)
    {
        _identifierAllow.Alter(identifier, alter);
    }
    
    public void AlterBlock(Identifier identifier, bool alter)
    {
        _identifierBlock.Alter(identifier, alter);
    }
}
