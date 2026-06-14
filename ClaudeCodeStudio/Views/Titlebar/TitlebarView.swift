import SwiftUI

struct TitlebarView: View {
    @EnvironmentObject var appState: AppState
    @State private var showSettings = false
    @State private var showAbout = false

    var body: some View {
        HStack(spacing: 0) {
            // Logo + Title
            HStack(spacing: 7) {
                Image(systemName: "brain.head.profile")
                    .font(.system(size: 14))
                    .foregroundColor(AppTheme.claudeAmber)

                Text("Claude Code Studio")
                    .font(.system(size: 12, weight: .semibold))
            }
            .frame(maxWidth: .infinity, alignment: .center)

            // User button
            Menu {
                Button("CLAUDE.md 长期记忆配置") { showSettings = true }
                Button("Claude 内核更新") { showAbout = true }
                Divider()
                Button("头像及昵称") { showSettings = true }
                Button("语言设置") { showSettings = true }
                Divider()
                Button("关于") { showAbout = true }
            } label: {
                HStack(spacing: 6) {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color(red: 0.39, green: 0.38, blue: 0.95),
                                         Color(red: 0.55, green: 0.36, blue: 0.96)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 22, height: 22)
                        .overlay(
                            Text("P")
                                .font(.system(size: 10, weight: .semibold))
                                .foregroundColor(.white)
                        )

                    Text("paultunggm-pixel")
                        .font(.system(size: 11))
                        .foregroundColor(AppTheme.textSecondary)
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 4)
                .background(Color.black.opacity(0.03))
                .clipShape(Capsule())
            }
            .fixedSize()
            .padding(.trailing, 8)
        }
        .frame(height: 48)
        .background(.ultraThinMaterial)
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
        .sheet(isPresented: $showAbout) {
            AboutView()
        }
    }
}

struct AboutView: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "brain.head.profile")
                .font(.system(size: 48))
                .foregroundColor(AppTheme.claudeAmber)
            Text("Claude Code Studio")
                .font(.title2).bold()
            Text("版本 1.0.0 (Build 1)")
                .font(.system(size: 11))
                .foregroundColor(.secondary)
            Text("macOS 原生 AI 编程助手")
                .font(.system(size: 11))
                .foregroundColor(.secondary)
            Divider().frame(width: 200)
            Text("基于 SwiftUI 构建，支持 OpenAI 兼容及 Anthropic 原生 API")
                .font(.system(size: 10))
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .frame(width: 280)
            Button("关闭") { dismiss() }
                .keyboardShortcut(.return)
        }
        .padding(40)
        .frame(width: 360, height: 320)
    }
}
