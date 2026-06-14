import SwiftUI

@main
struct ClaudeCodeStudioApp: App {
    @StateObject private var appState: AppState
    @StateObject private var providerManager: ProviderManager
    @StateObject private var projectManager: ProjectManager
    @StateObject private var chatManager: ChatManager

    init() {
        let app = AppState()
        let pm = ProviderManager()
        let proj = ProjectManager()
        let chat = ChatManager()
        chat.providerManager = pm
        chat.projectManager = proj
        chat.fixOrphanedSessions()
        _appState = StateObject(wrappedValue: app)
        _providerManager = StateObject(wrappedValue: pm)
        _projectManager = StateObject(wrappedValue: proj)
        _chatManager = StateObject(wrappedValue: chat)
    }

    var body: some Scene {
        Window("Claude Code Studio", id: "main") {
            ContentView()
                .environmentObject(appState)
                .environmentObject(providerManager)
                .environmentObject(projectManager)
                .environmentObject(chatManager)
                .frame(minWidth: 960, idealWidth: 1440, minHeight: 640, idealHeight: 900)
        }
        .windowStyle(.titleBar)
        .windowToolbarStyle(.unified)
    }
}
