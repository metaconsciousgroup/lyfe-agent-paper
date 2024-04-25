using Sirenix.OdinInspector;
using UnityEngine;

public class CharacterAnimatorStateMachine : StateMachineBehaviour
{
    [SerializeField] private int _idles;

    [ReadOnly, ShowInInspector] private float _normalizedTime;
    [ReadOnly, ShowInInspector] private float _normalizedTimeCycle;
    [ReadOnly, ShowInInspector] private float _length;
    [ReadOnly, ShowInInspector] private float _speed;
    
    
    private static readonly int Idle = Animator.StringToHash("Idle");

    public override void OnStateEnter(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    {
        RandomizeIdleVariant(animator);
    }
 
    public override void OnStateUpdate(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    {
        _normalizedTime = stateInfo.normalizedTime;
        _length = stateInfo.length;
        _speed = stateInfo.speed;

        float a = stateInfo.normalizedTime % 1f;
        if (a < _normalizedTimeCycle)
        {
            RandomizeIdleVariant(animator);
        }
        _normalizedTimeCycle = a;
    }
 
    public override void OnStateExit(Animator animator, AnimatorStateInfo stateInfo, int layerIndex)
    {

    }

    private void RandomizeIdleVariant(Animator animator)
    {
        animator.SetFloat(Idle, Random.Range(0, _idles + 1) / (float)_idles);
    }

}
