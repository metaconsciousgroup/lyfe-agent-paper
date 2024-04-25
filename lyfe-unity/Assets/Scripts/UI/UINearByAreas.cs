using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class UINearByAreas : UIMonoBehaviour
{
    [SerializeField] private NearByAreas _nearByAreas;
    [SerializeField] private UIContent _content;

    private Dictionary<LyfeCreatorWorldArea, UIContentElementNearByArea> _map = new();
    
    protected override void Awake()
    {
        base.Awake();
        Set(_nearByAreas);
    }

    public void Set(NearByAreas value)
    {
        Clear();
        _nearByAreas = value;
        
        if (value == null) return;
        
        Add(_nearByAreas.GetAll().ToArray());
        AlterNearByListeners(true);
    }
    
    public void OnNearByAreaEnter(LyfeCreatorWorldArea character)
    {
        Add(character);
    }
    
    public void OnNearByAreaExit(LyfeCreatorWorldArea character)
    {
        Remove(character);
    }


    private void Add(params LyfeCreatorWorldArea[] areas)
    {
        if (areas == null) return;
        int length = areas.Length;

        for (int i = 0; i < length; i++)
        {
            LyfeCreatorWorldArea area = areas[i];
            if (area == null) continue;
            if(_map.ContainsKey(area)) continue;

            UIContentElementNearByArea element = _content.Create<UIContentElementNearByArea>();
            _map.Add(area, element);
            element.SetArea(area);
        }
    }

    private void Remove(params LyfeCreatorWorldArea[] areas)
    {
        if (areas == null) return;
        int length = areas.Length;

        for (int i = 0; i < length; i++)
        {
            LyfeCreatorWorldArea character = areas[i];
            if (character == null) continue;
            if(!_map.ContainsKey(character)) continue;

            UIContentElementNearByArea element = _map[character];
            if(element != null) Destroy(element.gameObject);
            _map.Remove(character);
        }
    }

    public void Clear()
    {
        AlterNearByListeners(false);
        _nearByAreas = null;
        _map.Clear();
        _content.Clear();
    }

    private void AlterNearByListeners(bool alter)
    {
        if (_nearByAreas == null) return;
        _nearByAreas.onEnter.AlterListener(OnNearByAreaEnter, alter);
        _nearByAreas.onExit.AlterListener(OnNearByAreaExit, alter);
    }
}
