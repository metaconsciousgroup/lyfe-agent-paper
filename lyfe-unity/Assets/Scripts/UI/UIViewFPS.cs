using System.Collections;
using Sirenix.OdinInspector;
using TMPro;
using UnityEngine;

public class UIViewFPS : UIView
{
    [SerializeField] private float _refreshRate = 0.1f;
    [SerializeField] private TMP_Text _tmp;
    [ReadOnly, ShowInInspector] private float _fps;

    protected override void Start()
    {
        base.Start();
        StartCoroutine(Handler());
        
        IEnumerator Handler()
        {
            while (IsPlaying())
            {
                _fps = 1f / Time.unscaledDeltaTime;
                if (_tmp != null) _tmp.text = Mathf.FloorToInt(_fps).ToString();
                yield return new WaitForSeconds(_refreshRate);
            }
        }
    }

    protected override void OnGroupOpened()
    {
        
    }

    protected override void OnGroupClosed()
    {
        
    }
}
