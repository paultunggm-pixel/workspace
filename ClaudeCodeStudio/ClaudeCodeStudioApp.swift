import SwiftUI
@main
struct ClaudeCodeStudioApp: App {
    @StateObject private var appState = AppState()
    var body: some Scene {
        Window("Claude Code Studio", id:"main") {
            ContentView().environmentObject(appState)
                .frame(minWidth:960,idealWidth:1440,minHeight:640,idealHeight:900)
        }.windowStyle(.titleBar).windowToolbarStyle(.unified)
    }
}
