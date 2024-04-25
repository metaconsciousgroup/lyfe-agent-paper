
public class UIViewServer : UIView
{
    
    protected override void OnGroupOpened()
    {
        
    }

    protected override void OnGroupClosed()
    {
        
    }

    public void OnButtonClientStart()
    {
        App.Instance.GetGame().GetNetwork().StartClient();
    }
    
    public void OnButtonClientStop()
    {
        App.Instance.GetGame().GetNetwork().StopClient();
    }

    public void OnButtonDisconnectAllPlayers()
    {
        App.Instance.GetGame().GetNetwork().DisconnectAllClients(false);
    }
}
