// swift-tools-version:5.10
import PackageDescription

let package = Package(
    name: "ClaudeCodeStudio",
    platforms: [.macOS(.v13)],
    products: [
        .executable(name: "ClaudeCodeStudio", targets: ["ClaudeCodeStudio"])
    ],
    targets: [
        .executableTarget(
            name: "ClaudeCodeStudio",
            path: ".",
            sources: [
                "ClaudeCodeStudioApp.swift",
                "ContentView.swift",
                "Models/AppState.swift",
                "Models/Provider.swift",
                "Models/ProjectModels.swift",
                "Models/ChatModels.swift",
                "Models/DeployModels.swift",
                "Models/ServiceModels.swift",
                "Services/KeychainManager.swift",
                "Services/ProviderManager.swift",
                "Services/ProjectManager.swift",
                "Services/ChatManager.swift",
                "Services/APIService.swift",
                "Theme/AppTheme.swift",
                "Views/Sidebar/SidebarView.swift",
                "Views/Sidebar/ModelSelector.swift",
                "Views/Sidebar/QuickSwitchButtons.swift",
                "Views/Sidebar/BalanceCard.swift",
                "Views/Sidebar/ProjectTreeView.swift",
                "Views/Content/ContentArea.swift",
                "Views/Content/TabBar.swift",
                "Views/Content/ChatTabView.swift",
                "Views/Content/PlanTabView.swift",
                "Views/Content/PreviewTabView.swift",
                "Views/Content/CodeTabView.swift",
                "Views/Content/PublishTabView.swift",
                "Views/Content/ServiceTabView.swift",
                "Views/Settings/SettingsView.swift",
                "Views/Titlebar/TitlebarView.swift",
                "Views/StatusBar/StatusBarView.swift"
            ],
            swiftSettings: [.define("MACOS_14_DEPLOY")]
        )
    ]
)
