using UnityEngine;

[CreateAssetMenu(fileName = "Lyfe Creator Settings", menuName = "SO/App/Creator/Settings", order = 1)]
public class SOLyfeCreatorSettings : SO
{
    [SerializeField] private Area _area;
    [SerializeField] private Shape _shape;


    public Area GetArea() => _area;
    public Shape GetShape() => _shape;
    
    
    [System.Serializable]
    public class Area
    {
        [SerializeField] private SOValueColor _color;
        [SerializeField] private GameObject _prefab;

        [SerializeField] private string _layerName;

        public SOValueColor GetColor() => _color;
        public GameObject GetPrefab() => _prefab;

        public string GetLayerName() => _layerName;
    }
    
    [System.Serializable]
    public class Shape
    {
        [SerializeField] private Sprite _spriteCircle;
        [SerializeField] private Sprite _spriteRect;

        public Sprite GetSpriteCircle() => _spriteCircle;
        public Sprite GetSpriteRect() => _spriteRect;
    }
}
