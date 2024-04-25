using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class UINearByCharacters : UIMonoBehaviour
{
    [SerializeField] private NearByCharacters _nearByCharacters;
    [SerializeField] private UIContent _content;

    private Dictionary<CharacterEntity, UIContentElementNearByCharacter> _map = new();


    protected override void Awake()
    {
        base.Awake();
        Set(_nearByCharacters);
    }

    public void Set(NearByCharacters value)
    {
        Clear();
        _nearByCharacters = value;
        
        if (value == null) return;
        
        Add(_nearByCharacters.GetAll().ToArray());
        AlterNearByListeners(true);
    }
    
    public void OnNearByCharacterEnter(CharacterEntity character)
    {
        Add(character);
    }
    
    public void OnNearByCharacterExit(CharacterEntity character)
    {
        Remove(character);
    }


    private void Add(params CharacterEntity[] characters)
    {
        if (characters == null) return;
        int length = characters.Length;

        for (int i = 0; i < length; i++)
        {
            CharacterEntity character = characters[i];
            if (character == null) continue;
            if(_map.ContainsKey(character)) continue;

            UIContentElementNearByCharacter element = _content.Create<UIContentElementNearByCharacter>();
            _map.Add(character, element);
            element.SetCharacter(character);
        }
    }

    private void Remove(params CharacterEntity[] characters)
    {
        if (characters == null) return;
        int length = characters.Length;

        for (int i = 0; i < length; i++)
        {
            CharacterEntity character = characters[i];
            if (character == null) continue;
            if(!_map.ContainsKey(character)) continue;

            UIContentElementNearByCharacter element = _map[character];
            if(element != null) Destroy(element.gameObject);
            _map.Remove(character);
        }
    }

    public void Clear()
    {
        AlterNearByListeners(false);
        _nearByCharacters = null;
        _map.Clear();
        _content.Clear();
    }

    private void AlterNearByListeners(bool alter)
    {
        if (_nearByCharacters == null) return;
        _nearByCharacters.onEnter.AlterListener(OnNearByCharacterEnter, alter);
        _nearByCharacters.onExit.AlterListener(OnNearByCharacterExit, alter);
    }

    
}
