using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;
using System.IO;
using System.Runtime.InteropServices;
using UnityEditor.AddressableAssets.Settings;
using UnityEditor.AddressableAssets;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

public class ExtendedBuildScript
{
    private const string macOSBuildFolderPath = "Builds/macOS/";
    private const string webGLBuildFolderPath = "Builds/WebGL/";
    private const string linuxBuildFolderPath = "Builds/Linux/";
    private const string windowsBuildFolderPath = "Builds/Windows/";
    private const string CompanyName = "LyfeGame Inc.";
    private const string ProductName = "LyfeGame";
    private const string MainConfigPath = "Assets/Configs/Environment/";
    private const string ConfigDataPath = MainConfigPath + "Data/";
    private const string HostConfigPath = ConfigDataPath + "App Config Environment - Server.asset";
    private const string ClientConfigPath = ConfigDataPath + "/App Config Environment - Client.asset";
    private const string DevelopmentConfigPath = ConfigDataPath + "App Config Environment - Development.asset";

    private const string clientBuildName = "LyfeGameClient";
    private static readonly string[] Scenes = new[] {
        "Assets/Scenes/Init.unity",
        "Assets/Scenes/Main Menu/Main Menu.unity",
    };

    private static void UpdateScriptableObjectForBuild(string path)
    {
        // Path to the main SOAppConfig asset
        string soAppConfigPath = MainConfigPath + "App Config.asset";

        // Load the main SOAppConfig asset
        SOAppConfig mainConfig = AssetDatabase.LoadAssetAtPath<SOAppConfig>(soAppConfigPath);

        if (mainConfig == null)
        {
            throw new System.Exception($"Failed to load main SOAppConfig asset at {soAppConfigPath}");
        }

        // Load the SOAppConfigEnvironment asset
        SOAppConfigEnvironment environment = AssetDatabase.LoadAssetAtPath<SOAppConfigEnvironment>(path);

        if (environment == null)
        {
            throw new UnityException($"Failed to load {nameof(SOAppConfigEnvironment)} from path '{path}'");
        }

        mainConfig.SetEnvironment(environment);
        EditorUtility.SetDirty(mainConfig);
        AssetDatabase.SaveAssets();
    }


    [MenuItem("Build/Build macOS development build")]
    public static void BuildMacOSDevelopment()
    {
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = Scenes,
            locationPathName = macOSBuildFolderPath + "LyfeGame_Development.app",
            target = BuildTarget.StandaloneOSX,
            targetGroup = BuildTargetGroup.Standalone,
            options = BuildOptions.CompressWithLz4HC
        };
        EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Standalone, BuildTarget.StandaloneOSX);
        EditorUserBuildSettings.standaloneBuildSubtarget = StandaloneBuildSubtarget.Player;
        PlayerSettings.SetArchitecture(BuildTargetGroup.Standalone, (int)Architecture.Arm64);
        UpdateScriptableObjectForBuild(DevelopmentConfigPath);
        BuildForPlatform(buildOptions);
    }

    [MenuItem("Build/Build macOS host build")]
    public static void BuildMacOSHost()
    {
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = Scenes,
            locationPathName = macOSBuildFolderPath + "LyfeGame_Host.app",
            target = BuildTarget.StandaloneOSX,
            targetGroup = BuildTargetGroup.Standalone,
            options = BuildOptions.CompressWithLz4HC
        };
        EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Standalone, BuildTarget.StandaloneOSX);
        EditorUserBuildSettings.standaloneBuildSubtarget = StandaloneBuildSubtarget.Player;
        PlayerSettings.SetArchitecture(BuildTargetGroup.Standalone, (int)Architecture.Arm64);
        UpdateScriptableObjectForBuild(HostConfigPath);
        BuildForPlatform(buildOptions);
    }

    [MenuItem("Build/Build macOS client build")]
    public static void BuildMacOSClient()
    {
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = Scenes,
            locationPathName = macOSBuildFolderPath + clientBuildName + ".app",
            target = BuildTarget.StandaloneOSX,
            targetGroup = BuildTargetGroup.Standalone,
            options = BuildOptions.CompressWithLz4HC
        };
        EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Standalone, BuildTarget.StandaloneOSX);
        EditorUserBuildSettings.standaloneBuildSubtarget = StandaloneBuildSubtarget.Player;
        PlayerSettings.SetArchitecture(BuildTargetGroup.Standalone, (int)Architecture.Arm64);
        UpdateScriptableObjectForBuild(ClientConfigPath);
        BuildForPlatform(buildOptions);
    }

    [MenuItem("Build/Build WebGL Client")]
    public static void BuildWebGLClient()
    {
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = Scenes,
            locationPathName = webGLBuildFolderPath + clientBuildName,
            target = BuildTarget.WebGL,
            targetGroup = BuildTargetGroup.WebGL,
            options = BuildOptions.CompressWithLz4HC
        };
        EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.WebGL, BuildTarget.WebGL);
        PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Brotli;
        UpdateScriptableObjectForBuild(ClientConfigPath);
        BuildForPlatform(buildOptions);
    }

    [MenuItem("Build/Build Windows Client")]
    public static void BuildWindowsClient()
    {
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = Scenes,
            locationPathName = windowsBuildFolderPath + clientBuildName + ".exe",
            target = BuildTarget.StandaloneWindows64,
            targetGroup = BuildTargetGroup.Standalone,
            options = BuildOptions.CompressWithLz4HC
        };
        EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Standalone, BuildTarget.StandaloneWindows64);
        EditorUserBuildSettings.standaloneBuildSubtarget = StandaloneBuildSubtarget.Player;
        UpdateScriptableObjectForBuild(ClientConfigPath);
        BuildForPlatform(buildOptions);
    }

    [MenuItem("Build/Build Linux Dedicated Server")]
    public static void BuildLinuxDedicatedServer()
    {
        BuildPlayerOptions buildOptions = new BuildPlayerOptions
        {
            scenes = Scenes,
            locationPathName = linuxBuildFolderPath + "LyfeGameServer",
            target = BuildTarget.StandaloneLinux64,
            targetGroup = BuildTargetGroup.Standalone,
            subtarget = (int)StandaloneBuildSubtarget.Server,
            options = BuildOptions.CompressWithLz4HC
        };
        EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Standalone, BuildTarget.StandaloneLinux64);
        EditorUserBuildSettings.standaloneBuildSubtarget = StandaloneBuildSubtarget.Server;
        UpdateScriptableObjectForBuild(HostConfigPath);
        BuildForPlatform(buildOptions);
    }

    [MenuItem("Build/Build Addressables")]
    private static void BuildAddressables()
    {
        // Build the Addressable Asset bundles
        AddressableAssetSettings.CleanPlayerContent(AddressableAssetSettingsDefaultObject.Settings.ActivePlayerDataBuilder);
        AddressableAssetSettings.BuildPlayerContent();
    }
    [MenuItem("Build/Build All")]
    public static void BuildAllTargets()
    {
        DiscardUnsavedChanges();
        BuildAddressables();
        BuildMacOSDevelopment();
        BuildMacOSHost();
        BuildLinuxDedicatedServer();
        BuildMacOSClient();
        BuildWebGLClient();
        BuildWindowsClient();
    }

    private static void BuildForPlatform(BuildPlayerOptions buildOptions)
    {
        string buildPath = buildOptions.locationPathName;

        // Remove the existing build if it exists
        if (Directory.Exists(buildPath))
        {
            Directory.Delete(buildPath, true);
            File.Delete(buildPath + ".meta");
        }

        PlayerSettings.companyName = CompanyName;
        PlayerSettings.productName = ProductName;

        BuildReport report = BuildPipeline.BuildPlayer(buildOptions);
        HandleBuildReport(report, buildPath);
    }

    private static void HandleBuildReport(BuildReport report, string buildPath)
    {
        BuildSummary summary = report.summary;

        if (summary.result == BuildResult.Succeeded)
        {
            Debug.Log($"Build succeeded at {buildPath}: " + summary.totalSize + " bytes");
        }

        if (summary.result == BuildResult.Failed)
        {
            Debug.LogError("Build failed");
        }

        Debug.Log(report);
        string detailedReport = GetDetailedBuildReport(report);
        File.WriteAllText(buildPath + "_BuildReport.txt", detailedReport);
    }


    private static string GetDetailedBuildReport(BuildReport report)
    {
        System.Text.StringBuilder sb = new System.Text.StringBuilder();

        sb.AppendLine("Build Report:");
        sb.AppendLine("-------------");
        sb.AppendLine($"Build Date: {System.DateTime.Now}");
        sb.AppendLine($"Total Errors: {report.summary.totalErrors}");
        sb.AppendLine($"Total Warnings: {report.summary.totalWarnings}");
        sb.AppendLine($"Total Time: {report.summary.totalTime} seconds");
        sb.AppendLine($"Total Size: {BytesToReadableSize(report.summary.totalSize)}");
        sb.AppendLine($"Build Result: {report.summary.result}");

        sb.AppendLine("\nSteps:");
        foreach (var step in report.steps)
        {
            sb.AppendLine($"- {step.name} ({step.duration}s)");
            foreach (var msg in step.messages)
            {
                sb.AppendLine($"  [{msg.type}] {msg.content}");
            }
        }

        sb.AppendLine("\nFiles included:");
        foreach (var file in report.GetFiles())
        {
            sb.AppendLine($"- {file.path} ({BytesToReadableSize(file.size)}, {file.role})");
        }

        return sb.ToString();
    }

    private static string BytesToReadableSize(ulong bytes)
    {
        string[] sizeSuffixes = { "bytes", "KB", "MB", "GB", "TB" };
        int i;
        double doubleBytes = bytes;

        for (i = 0; i < sizeSuffixes.Length && doubleBytes >= 1024; i++)
        {
            doubleBytes /= 1024;
        }

        return $"{doubleBytes:0.##} {sizeSuffixes[i]}";
    }

    [MenuItem("Build/Discard Unsaved Changes")]
    private static void DiscardUnsavedChanges()
    {
        for (int i = 0; i < SceneManager.sceneCount; i++)
        {
            Scene scene = SceneManager.GetSceneAt(i);
            if (scene.isDirty)
            {
                // Reloads the scene from the last saved state
                EditorSceneManager.OpenScene(scene.path, OpenSceneMode.Single);
            }
        }
        AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
    }
}
