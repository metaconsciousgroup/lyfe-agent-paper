using UnityEngine;

[CreateAssetMenu(fileName = "Development Scene - ", menuName = "SO/App/Development Scene", order = 1)]
public class SODevelopmentScene : SO
{
    [SerializeField] private string _title;
    [SerializeField] private Sprite _image;
    [SerializeField] private SOScene _scene;

    public string GetTitle() => _title;
    public Sprite GetImage() => _image;
    public SOScene GetScene() => _scene;
}
