
public class UIViewLobbyClient : UIViewLobby
{
    protected override string GetSceneOverride() => null;
    
    protected override void OnGroupOpened()
    {
        Clear();
    }

    protected override void OnGroupClosed()
    {
        Clear();
    }
}
