using Sirenix.OdinInspector;
using UnityEngine;

public class LyfeCreatorWorldArea : BaseMonoBehaviour
{
    [ReadOnly, ShowInInspector] private string _key;
    [ReadOnly, ShowInInspector] private LyfeCreatorWorldShape _shape;
    [ReadOnly, ShowInInspector] private SOLyfeCreatorSettings _settings;
    [SerializeField] private MinimapMarker _minimapMarker;

    public string GetKey() => _key;

    public Vector3 GetPoint() => _shape == null ? transform.position : _shape.GetPoint();

    public void SetData(LyfeCreatorDataWorldArea data, SOLyfeCreatorSettings settings)
    {
        _key = data.key;
        _settings = settings;
        _minimapMarker.SetColor(_settings.GetArea().GetColor());

        // Shape does not exist
        if (data.shape == null)
        {
            // Kill existing shape
            if (_shape != null)
            {
                Destroy(_shape);
                _shape = null;
            }
            _minimapMarker.SetVisibleNo();
        }

        // Shape exists
        else
        {
            // Create shape component if doesnt exist
            if (_shape == null)
            {
                _shape = gameObject.AddComponent<LyfeCreatorWorldShape>();
            }
            _shape.SetData(data.shape);

            // Setup minimap
            switch (data.shape.kind)
            {
                case LyfeCreatorWorldShapeKind.Circle:
                case LyfeCreatorWorldShapeKind.Sphere:
                    {
                        float s = data.shape.radiusMax;
                            _minimapMarker
                                .SetSize(s, s)
                                .SetSprite(_settings.GetShape().GetSpriteCircle())
                                .SetVisibleYes();
                        break;
                    }
                case LyfeCreatorWorldShapeKind.Rect:
                    {
                        _minimapMarker
                            .SetSize(data.shape.sizeMax.x * 0.5f, data.shape.sizeMax.z * 0.5f)
                            .SetSprite(_settings.GetShape().GetSpriteRect())
                            .SetVisibleYes();
                        break;
                    }
                default:
                    {
                        _minimapMarker.SetVisibleNo();
                        break;
                    }
            }
        }

        Transform target = data.targetTransform;
        transform.position = target.position;
        transform.rotation = target.rotation;
    }

}
