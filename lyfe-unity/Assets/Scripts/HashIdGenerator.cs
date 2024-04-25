using System.Text;

public class HashIdGenerator
{
    private string _characters;
    private int _length;

    public HashIdGenerator(int length): this(length, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") { }
    
    public HashIdGenerator(int length, string characters)
    {
        _characters = characters;
        _length = length;
    }
    
    
    public string Generate()
    {
        StringBuilder sb = new StringBuilder(_length);
        int l = _characters.Length;
        for (int i = 0; i < _length; i++) sb.Append(_characters[UnityEngine.Random.Range(0, l)]);
        return sb.ToString();
    }
}
