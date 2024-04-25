using UnityEngine;

public class MinimapMarker : MonoBehaviour
{
    [SerializeField] private UIImage _image;
    [SerializeField] private ApplyGraphicSOValueColor _applyColor;


    public MinimapMarker SetSprite(Sprite value)
    {
        _image.sprite = value;
        return this;
    }
    
    public MinimapMarker SetColor(SOValueColor value)
    {
        _applyColor.SetSO(value);
        return this;
    }

    public MinimapMarker SetSize(float x, float z)
    {
        _image.transform.localScale = new Vector3(x, z, 1f);
        return this;
    }
    
    public void SetVisibleYes()
    {
        SetVisible(true);
    }

    public void SetVisibleNo()
    {
        SetVisible(false);
    }

    public void SetVisible(bool isActive)
    {
        gameObject.SetActive(isActive);
    }
    
}
