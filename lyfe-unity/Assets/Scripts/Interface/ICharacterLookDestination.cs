using UnityEngine;

public interface ICharacterLookDestination
{
    /// <summary>
    /// Returns optional look at point, true if point is ready.
    /// Optional case can happen when target look at is set but not initialized yet, for example avatar has not yet loaded.
    /// </summary>
    /// <param name="point"></param>
    /// <returns></returns>
    public bool GetLookAtDestinationPoint(out Vector3 point);

    public abstract Transform transform { get; }
}
