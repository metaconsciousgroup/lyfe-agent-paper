using System.Collections.Generic;
using UnityEngine;

public class SpriteBuilder : BaseMonoBehaviour
{
    [SerializeField] private float _pixelsPerUnit;
    [SerializeField] private Vector2 _pivot;
    [SerializeField] private uint _extrude;
    [SerializeField] private SpriteMeshType _spriteMeshType;

    public Texture2D[] tests;
    public List<Sprite> results;

#if UNITY_EDITOR
    protected override void Reset()
    {
        base.Reset();
        _pixelsPerUnit = 100f;
        _pivot = new Vector2(0.5f, 0.5f);
        _extrude = 0;
        _spriteMeshType = SpriteMeshType.FullRect;
    }
#endif

    protected override void Start()
    {
        base.Start();
        foreach (Texture2D texture2D in tests)
        {
            results.Add(Get(texture2D));
        }
    }

    public Sprite Get(Texture2D texture)
    {
        return Get(texture, _pivot, _pixelsPerUnit, _extrude, _spriteMeshType);
    }
    
    public Sprite Get(Texture2D texture, Vector2 pivot, float pixelsPerUnit, uint extrude, SpriteMeshType spriteMeshType)
    {
        Rect rect = new Rect(0, 0, texture.width, texture.height);
        Sprite sprite = Sprite.Create(texture, rect, pivot, pixelsPerUnit, extrude, spriteMeshType);
        return sprite;
    }
}
