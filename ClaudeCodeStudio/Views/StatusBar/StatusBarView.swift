import SwiftUI

struct StatusBarView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        HStack {
            // GitHub status - reads from AppState
            HStack(spacing: 6) {
                Text("🐙")
                Text(appState.gitBranch)
                    .font(.system(size: 9, design: .monospaced))
                if !appState.gitLastCommit.isEmpty {
                    Text("·")
                    Text(appState.gitLastCommit.prefix(7))
                }
            }
            .font(.system(size: 9))
            .foregroundColor(AppTheme.textTertiary)

            Spacer()

            // Engine & Token status
            HStack(spacing: 10) {
                Text("Claude Code Studio")
                Text("Tokens \(appState.tokenCount)/\(appState.tokenLimit)")
            }
            .font(.system(size: 9))
            .foregroundColor(AppTheme.textTertiary)
        }
        .padding(.horizontal, 14)
        .frame(height: 28)
        .background(.ultraThinMaterial)
        .overlay(
            Rectangle()
                .frame(height: 1)
                .foregroundColor(AppTheme.dividerGray),
            alignment: .top
        )
    }
}
