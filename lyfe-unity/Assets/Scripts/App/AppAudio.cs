using UnityEngine;

public class AppAudio : MonoBehaviour
{
    [SerializeField] private AudioPlayer _buttonClick;
    [SerializeField] private AudioPlayer _buttonBack;
    [SerializeField] private AudioPlayer _buttonHover;

    public AudioPlayer GetButtonClick() => _buttonClick;
    public AudioPlayer GetButtonBack() => _buttonBack;
    public AudioPlayer GetButtonHover() => _buttonHover;
}
