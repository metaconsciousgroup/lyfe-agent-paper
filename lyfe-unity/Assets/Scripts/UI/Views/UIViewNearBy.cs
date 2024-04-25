using UnityEngine;

public class UIViewNearBy : UIView
{
    [Header(H_L + "Near By" + H_R)]
    [SerializeField] private UINearByCharacters _nearByCharacters;
    [SerializeField] private UINearByAreas _nearByAreas;
    
    protected override void OnGroupOpened()
    {
        
    }

    protected override void OnGroupClosed()
    {
        
    }

    public void Set(CharacterEntity character)
    {
        if (character == null)
        {
            Clear();
            return;
        }
        
        _nearByCharacters.Set(character.GetNearByCharacters());
        _nearByAreas.Set(character.GetNearByAreas());
    }

    public void Clear()
    {
        _nearByCharacters.Clear();
        _nearByAreas.Clear();
    }
}
