using UnityEngine.Events;

/// <summary>
/// Data object holding single button information for info popup view.
/// </summary>
public class InfoPopupButtonData
{
    /// <summary>
    /// Button title.
    /// </summary>
    public string title;
    /// <summary>
    /// Event callback on button press.
    /// </summary>
    public UnityAction onClick;
    /// <summary>
    /// Should view auto close on button press.
    /// </summary>
    public bool autoCloseWindowOnClick;
        
    public InfoPopupButtonData(){}

    /// <summary>
    /// Constructor
    /// </summary>
    /// <param name="title">Button title.</param>
    public InfoPopupButtonData(string title)
    {
        this.title = title;
        this.onClick = null;
        this.autoCloseWindowOnClick = true;
    }

    /// <summary>
    /// Constructor
    /// </summary>
    /// <param name="title">Button title.</param>
    /// <param name="onClick">Event callback on button press.</param>
    public InfoPopupButtonData(string title, UnityAction onClick)
    {
        this.title = title;
        this.onClick = onClick;
        this.autoCloseWindowOnClick = true;
    }
        
    /// <summary>
    /// 
    /// </summary>
    /// <param name="title">Button title.</param>
    /// <param name="onClick">Event callback on button press.</param>
    /// <param name="autoCloseWindowOnClick">Should view auto close on button press.</param>
    public InfoPopupButtonData(string title, UnityAction onClick, bool autoCloseWindowOnClick)
    {
        this.title = title;
        this.onClick = onClick;
        this.autoCloseWindowOnClick = autoCloseWindowOnClick;
    }
    
    /// <summary>
    /// Returns new instance.
    /// </summary>
    /// <param name="title">Button title.</param>
    /// <returns></returns>
    public static InfoPopupButtonData From(string title) => new(title);

    /// <summary>
    /// Returns new instance.
    /// </summary>
    /// <param name="title">Button title.</param>
    /// <param name="onClick">Event callback on button press.</param>
    /// <returns></returns>
    public static InfoPopupButtonData From(string title, UnityAction onClick) => new(title, onClick);
    
    /// <summary>
    /// Returns new instance.
    /// </summary>
    /// <param name="title">Button title.</param>
    /// <param name="onClick">Event callback on button press.</param>
    /// <param name="autoCloseWindowOnClick">Should view auto close on button press.</param>
    /// <returns></returns>
    public static InfoPopupButtonData From(string title, UnityAction onClick, bool autoCloseWindowOnClick) => new(title, onClick, autoCloseWindowOnClick);
}
