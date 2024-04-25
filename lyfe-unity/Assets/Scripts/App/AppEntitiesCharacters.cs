using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.Events;

public class AppEntitiesCharacters : BaseMonoBehaviour
{
    [SerializeField] private CharacterEntity _prefab;

    [SerializeField] private UnityEvent<CharacterEntity> _onCreated;

    [Button]
    public List<CharacterEntity> GetAll() => transform.GetComponentsPro<CharacterEntity>(GetComponentProExtensions.Scan.Down, 1, 0);

    public CharacterEntity Create(InDataAgent value) => Create(value.user, value.character, value.transform);

    public CharacterEntity Create(InDataUser userData, InDataCharacter characterData, TransformData transformData)
    {
        return Create(
            userData.id,
            userData.username,
            characterData.modelPath,
            transform,
            transformData.position.GetVector3(),
            transformData.rotation.GetVector3(),
            Vector3.one
            );
    }

    public CharacterEntity Create(
        string id,
        string username,
        string characterModelPath,
        Transform parent,
        Vector3 localPosition,
        Vector3 localRotation,
        Vector3 localScale
        )
    {
        CharacterEntity character = Instantiate(_prefab);
        Transform tr = character.transform;
        tr.SetParent(parent, localPosition, Quaternion.Euler(localRotation), localScale);

        _onCreated.Invoke(character);
        return character;
    }

    public bool GetById(string id, out CharacterEntity character)
    {
        character = null;
        if (string.IsNullOrEmpty(id)) return false;
        
        foreach (CharacterEntity i in transform.GetComponentsPro<CharacterEntity>(GetComponentProExtensions.Scan.Down, 1, 0))
        {
            if (i.GetClient().GetSyncId() == id)
            {
                character = i;
                break;
            }
        }
        return character != null;
    }
}
