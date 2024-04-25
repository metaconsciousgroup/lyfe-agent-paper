using System.Collections.Generic;
using System.Linq;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;

public abstract class NearBy<T> : BaseMonoBehaviour where T : BaseMonoBehaviour
{
    [SerializeField] private SphereCollider _sphereCollider;
    [SerializeField] private GameObject[] _blacklist;
    [SerializeField] private UnityEvent<T> _onEnter;
    [SerializeField] private UnityEvent<T> _onExit;
    
    [ReadOnly, ShowInInspector] private HashSet<T> _all = new HashSet<T>();

    public float GetRadius() => _sphereCollider.radius;
    public HashSet<T> GetAll() => _all;

    public UnityEvent<T> onEnter => _onEnter ??= new UnityEvent<T>();
    public UnityEvent<T> onExit => _onExit ??= new UnityEvent<T>();
    

    public void SetRadius(float value)
    {
        _sphereCollider.radius = value;
    }

    private void OnTriggerEnter(Collider other)
    {
        if (Enter(other.gameObject))
        {
            //Debug.Log($"Entered (OnTriggerEnter)");
        }
    }

    private void OnTriggerExit(Collider other)
    {
        if (Exit(other.gameObject))
        {
            //Debug.Log($"Exited (OnTriggerExit)");
        }
    }

    public bool Contains(T value)
    {
        if (value == null) return false;
        return _all.Contains(value);
    }

    private bool Enter(GameObject other)
    {
        if (new HashSet<GameObject>(_blacklist).Contains(other)) return false;

        if (!GetSource(other, out GameObject source)) return false;
        
        if (OnEnterCheck(source, out T target))
        {
            if (!_all.Contains(target))
            {
                _all.Add(target);
                target.onDestroy.AddListener(OnTargetDestroy);
                OnEntered(target);
                _onEnter.Invoke(target);
                return true;
            }
        }
        return false;
    }

    private bool Exit(GameObject other)
    {
        if (!GetSource(other, out GameObject source)) return false;
        return ExitSource(source);
    }

    private bool ExitSource(GameObject source)
    {
        if (OnExitCheck(source, out T target))
        {
            if (_all.Remove(target))
            {
                target.onDestroy.RemoveListener(OnTargetDestroy);
                OnExited(target);
                _onExit.Invoke(target);
                return true;
            }
        }
        return false;
    }

    private bool GetSource(GameObject other, out GameObject source)
    {
        source = null;
        TriggerTarget triggerTarget = other.GetComponent<TriggerTarget>();
        if (triggerTarget != null)
        {
            source = triggerTarget.GetTarget();
        }
        return source != null;
    }

    protected abstract bool OnEnterCheck(GameObject other, out T target);
    
    protected abstract bool OnExitCheck(GameObject other, out T target);
    
    protected abstract void OnEntered(T target);
    protected abstract void OnExited(T target);
    

    private void OnTargetDestroy(MonoBehaviour baseMonoBehaviour)
    {
        if (ExitSource(baseMonoBehaviour.gameObject))
        {
            //Debug.Log($"Exited (Destroyed)");
        }
    }
    
    public bool GetClosest(out T target)
    {
        target = null;
        List<T> all = GetAll().ToList();
        Vector3 currentPos = transform.position;
        target = all
            .OrderBy(i => Vector3.Distance(currentPos, i.transform.position)).FirstOrDefault();
        return target != null;
    }

}
