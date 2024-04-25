using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class AppUI : BaseMonoBehaviour
{
    [SerializeField] private CanvasScaler _canvasScaler;
    [SerializeField] private RectTransform _views;
    

    public T GetView<T>() where T : UIView
    {
        return _views.GetComponentPro<T>(GetComponentProExtensions.Scan.Down, 1, 0);
    }

    public List<UIView> GetViews()
    {
        return _views.GetComponentsPro<UIView>(GetComponentProExtensions.Scan.Down, 1, 0);
    }

    public void CloseAllViews()
    {
        foreach (UIView view in _views.GetComponentsInChildren<UIView>()) view.ToggleGroup(false);
    }

    public bool AnyOpen(params Type[] types)
    {
        HashSet<Type> set = new HashSet<Type>(types);
        
        foreach (UIView view in GetViews())
        {
            if (set.Contains(view.GetType()))
            {
                if (view.GetGroup().GetIdentifier().Contains())
                {
                    return true;
                }
            }
        }
        return false;
    }
    
    public void CloseAllViewsExcept<T>() where T : UIView
    {
        foreach (UIView view in _views.GetComponentsInChildren<UIView>())
        {
            view.ToggleGroup(view is T);
        }
    }

    public bool PerformEscape()
    {
        List<UIView> views = GetViews();
        int length = views.Count;
        int max = length - 1;
        
        for (int i = max; i >= 0; i--)
        {
            UIView view = views[i];
            if (view.Escape()) return true;
        }
        return false;
    }

    public void OnPlayerCharacterChanged(CharacterEntity character)
    {
        bool valid = character != null;
        ToggleGameRelatedViews(valid);
    }

    public void HideLobby()
    {
        GetView<UIViewLobbyHost>().CloseGroup();
        GetView<UIViewLobbyClient>().CloseGroup();
    }
    
    private void ToggleGameRelatedViews(bool isActive)
    {
        //Debug.Log($"Toggling game related ui views: {isActive}");

        HideLobby();
        
        HashSet<Type> whitelist = new HashSet<Type>
        {
            typeof(UIViewChat),
            typeof(UIViewMinimap),
            typeof(UIViewNearBy),
            typeof(UIViewChatBubbles)
        };

        foreach (UIView view in GetViews())
        {
            bool contains = whitelist.Contains(view.GetType());

            if (contains)
            {
                view.ToggleGroup(isActive); 
            }
        }
    }

    public void SetReferenceResolutionY(float value)
    {
        Vector2 res = _canvasScaler.referenceResolution;
        res.y = value;
        _canvasScaler.referenceResolution = res;
    }
}
