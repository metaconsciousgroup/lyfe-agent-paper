using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

public class Smartphone : BaseMonoBehaviour
{
    [SerializeField] private MeshRenderer _meshRenderer;
    [SerializeField] private AudioPlayer _audioIncomingCall;

    private Material _screenMaterial;
    private Color _screenOnColor = Color.white;
    

    private Material GetScreenMaterial()
    {
        if (_screenMaterial == null)
        {
            List<Material> materials = new List<Material>(_meshRenderer.sharedMaterials);
            Material screen = Instantiate(materials[2]);
            materials[2] = screen;
            _meshRenderer.SetMaterials(materials);
            _screenMaterial = screen;
        }
        return _screenMaterial;
    }

    [Button]
    public Smartphone TogglePhoneScreen(bool inOn)
    {
        GetScreenMaterial().color = inOn ? _screenOnColor : Color.black;
        return this;
    }

    [Button]
    public Smartphone RandomizeScreenOnColor()
    {
        _screenOnColor = GetRandomScreenColor();
        GetScreenMaterial().color = _screenOnColor;
        return this;
    }

    [Button]
    public void PlayAudioIncomingCall() => _audioIncomingCall.Play();

    private Color GetRandomScreenColor() => new Color(Random.value, Random.value, Random.value);
    
    
}
