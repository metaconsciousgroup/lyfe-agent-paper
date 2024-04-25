
public class IdGenerator
{
    private int _current;

    public IdGenerator()
    {
        _current = 1;
    }
    
    public IdGenerator(int current)
    {
        _current = current;
    }

    public int Get()
    {
        int value = _current;
        _current++;
        return value;
    }
}
