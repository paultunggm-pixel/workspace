import SwiftUI

struct StatusBarView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        HStack {
            // GitHub status
            HStack(spacing: 6) {
                Text("🐙")
                Text(appState.gitBranch)
                    .font(.system(size: 9, design: .monospaced))
                Text("·")
                Text(appState.gitLastCommit)
            }
            .font(.system(size: 9))
            .foregroundColor(AppTheme.textTertiary)

            Spacer()

            // Engine & Token status
            HStack(spacing: 10) {
                Text("Engine v2.1.150")
                Text("Tokens \(appState.tokenCount)K/\(appState.tokenLimit/1000)K")
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
