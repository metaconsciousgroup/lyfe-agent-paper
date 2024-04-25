using UnityEngine;

public class SceneMainMenu : BaseMonoBehaviour
{
    [SerializeField] private Transform _cameraPivot;

    /// <summary>
    /// Returns camera location pivot for in the main menu scene.
    /// </summary>
    /// <returns></returns>
    public Transform GetCameraPivot() => _cameraPivot;
}
