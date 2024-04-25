
using UnityEngine;
using UnityEngine.AddressableAssets;
using FishNet.Managing.Scened;
using UnityEngine.SceneManagement;
using System.Linq;
using UnityEngine.ResourceManagement.AsyncOperations;
using UnityEngine.ResourceManagement.ResourceProviders;
using System.Collections.Generic;
using System;
using System.Collections;

public class AddressableSceneProcessor : DefaultSceneProcessor
{

    private readonly Dictionary<string, string> _addressableSceneNames = new Dictionary<string, string>
        {
            { "LevelCity - Day", "Assets/Scenes/Levels/Level - City - Day/LevelCity - Day.unity" },
            { "LevelCity - Night", "Assets/Scenes/Levels/Level - City - Night/LevelCity - Night.unity" }
        };

    private Dictionary<string, AsyncOperationHandle<SceneInstance>> _loadingScenes = new Dictionary<string, AsyncOperationHandle<SceneInstance>>();

    public override void BeginLoadAsync(string sceneName, LoadSceneParameters parameters)
    {
        Debug.Log($"{GetType().Name} BeginLoadAsync {sceneName}");
        if (_addressableSceneNames.ContainsKey(sceneName))
        {
            // This is needed because client can go back to main menu and then back to game scene
            UnloadSceneByName(sceneName);
            string address = _addressableSceneNames[sceneName];
            Debug.Log($"{GetType().Name} BeginLoadAsync {sceneName} address {address}");
            AsyncOperationHandle<SceneInstance> handle = Addressables.LoadSceneAsync(address, parameters);
            _loadingScenes.Add(sceneName, handle);
        }
        else
        {
            base.BeginLoadAsync(sceneName, parameters);
        }

    }
    public override void BeginUnloadAsync(Scene scene)
    {

        if (_addressableSceneNames.ContainsKey(scene.name))
        {
            UnloadSceneByName(scene.name);
        }
        else
        {
            base.BeginUnloadAsync(scene);
        }
    }

    private void UnloadSceneByName(string sceneName)
    {
        if (_loadingScenes.ContainsKey(sceneName))
        {
            AsyncOperationHandle<SceneInstance> handle = _loadingScenes[sceneName];
            if (handle.IsValid())
            {
                Addressables.Release(handle);
            }
            _loadingScenes.Remove(sceneName);
        }
    }

    public override bool IsPercentComplete()
    {
        foreach (var handle in _loadingScenes.Values)
        {
            if (!handle.IsDone)
            {
                return false;
            }
        }
        return true;
    }

    public override float GetPercentComplete()
    {
        float totalProgress = 0.0f;
        int count = _loadingScenes.Count;
        if (count == 0) return 1.0f; // No scenes to load

        foreach (var handle in _loadingScenes.Values)
        {
            totalProgress += handle.PercentComplete;
        }

        return totalProgress / count;
    }

    public override IEnumerator AsyncsIsDone()
    {
        foreach (var handle in _loadingScenes.Values)
        {
            yield return handle;
        }
    }
}